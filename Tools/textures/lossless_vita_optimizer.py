import os, re, glob
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
MAX_DIM = 4096
MAX_AREA = 16_777_216 # 4096 * 4096

def next_power_of_two(x):
    return 1 if x == 0 else 2**(x - 1).bit_length()

def parse_all_tscns(target_dir):
    tscns = {}
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.tscn') or file.endswith('.tres'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    tscns[path] = f.read()
    return tscns

def save_tscn(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_ext_resource_paths(content):
    exts = {}
    for match in re.finditer(r'\[ext_resource path="([^"]+)" type="Texture" id=([A-Za-z0-9_]+)\]', content):
        exts[match.group(2)] = match.group(1)
    return exts

class Packer:
    def __init__(self, max_dim=4096):
        self.max_dim = max_dim
        self.x = 0
        self.y = 0
        self.row_h = 0
        self.mapping = {}
        self.img = Image.new('RGBA', (max_dim, max_dim))
        
    def add(self, old_rect, region_img):
        w, h = region_img.size
        if self.x + w > self.max_dim:
            self.x = 0
            self.y += self.row_h
            self.row_h = 0
            
        if self.y + h > self.max_dim:
            return False
            
        self.img.paste(region_img, (self.x, self.y))
        new_rect = (self.x, self.y, w, h)
        self.mapping[old_rect] = new_rect
        
        self.x += w
        self.row_h = max(self.row_h, h)
        return True

def process_repacking(target_dir):
    tscns = parse_all_tscns(target_dir)
    usage_map = {}
    
    for tscn_path, content in tscns.items():
        exts = get_ext_resource_paths(content)
        blocks = re.split(r'\n(?=\[)', content)
        for block in blocks:
            if 'type="AtlasTexture"' in block:
                m_ext = re.search(r'atlas\s*=\s*ExtResource\(\s*([A-Za-z0-9_]+)\s*\)', block)
                if m_ext and m_ext.group(1) in exts:
                    res_path = exts[m_ext.group(1)]
                    m_rect = re.search(r'Rect2\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)', block)
                    if m_rect:
                        rect = tuple(map(float, [m_rect.group(1), m_rect.group(2), m_rect.group(3), m_rect.group(4)]))
                        if res_path not in usage_map:
                            usage_map[res_path] = []
                        usage_map[res_path].append((tscn_path, rect))
                            
            if 'type="StyleBoxTexture"' in block:
                m_ext = re.search(r'texture\s*=\s*ExtResource\(\s*([A-Za-z0-9_]+)\s*\)', block)
                if m_ext and m_ext.group(1) in exts:
                    res_path = exts[m_ext.group(1)]
                    m_rect = re.search(r'region_rect\s*=\s*Rect2\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)', block)
                    if m_rect:
                        rect = tuple(map(float, [m_rect.group(1), m_rect.group(2), m_rect.group(3), m_rect.group(4)]))
                        if res_path not in usage_map:
                            usage_map[res_path] = []
                        usage_map[res_path].append((tscn_path, rect))

            if block.startswith('[node') and 'region_rect' in block:
                m_ext = re.search(r'texture\s*=\s*ExtResource\(\s*([A-Za-z0-9_]+)\s*\)', block)
                if m_ext and m_ext.group(1) in exts:
                    res_path = exts[m_ext.group(1)]
                    m_rect = re.search(r'region_rect\s*=\s*Rect2\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)', block)
                    if m_rect:
                        rect = tuple(map(float, [m_rect.group(1), m_rect.group(2), m_rect.group(3), m_rect.group(4)]))
                        if res_path not in usage_map:
                            usage_map[res_path] = []
                        usage_map[res_path].append((tscn_path, rect))
    
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith('.png'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, target_dir)
                res_path = "res://" + rel_path.replace("\\", "/")
                
                try:
                    with Image.open(filepath) as img:
                        w, h = img.size
                        max_d = max(w, h)
                        # We also check if it's NPOT, but let's focus on massive ones for repacking
                        if max_d > MAX_DIM or (max_d > 4000):
                            area = w * h
                            print(f"Found massive texture: {res_path} ({w}x{h})")
                            
                            if res_path in usage_map and area <= MAX_AREA:
                                print("  Attempting lossless repack...")
                                unique_rects = set(r[1] for r in usage_map[res_path])
                                packer = Packer(MAX_DIM)
                                success = True
                                
                                sorted_rects = sorted(list(unique_rects), key=lambda r: r[3], reverse=True)
                                
                                for r in sorted_rects:
                                    x, y, rw, rh = map(int, r)
                                    region_img = img.crop((x, y, x+rw, y+rh))
                                    if not packer.add(r, region_img):
                                        success = False
                                        break
                                        
                                if success:
                                    # Force POT dimensions for ETC1 compatibility on Vita GLES2
                                    used_width = max(r[0] + r[2] for r in packer.mapping.values())
                                    used_height = packer.y + packer.row_h
                                    pot_width = next_power_of_two(used_width)
                                    pot_height = next_power_of_two(used_height)
                                    
                                    final_img = packer.img.crop((0, 0, pot_width, pot_height))
                                    final_img.save(filepath, optimize=True)
                                    print(f"  Successfully repacked {file} into {final_img.size} lossless POT atlas!")
                                    
                                    # Update tscns
                                    affected_tscns = set(r[0] for r in usage_map[res_path])
                                    for tscn_path in affected_tscns:
                                        content = tscns[tscn_path]
                                        blocks = re.split(r'\n(?=\[)', content)
                                        new_blocks = []
                                        exts = get_ext_resource_paths(content)
                                        target_ext_id = None
                                        for k, v in exts.items():
                                            if v == res_path:
                                                target_ext_id = k
                                                break
                                                
                                        for block in blocks:
                                            if target_ext_id and (f'ExtResource( {target_ext_id} )' in block or f'ExtResource("{target_ext_id}")' in block):
                                                def repl_all_rects(m):
                                                    cx, cy, cw, ch = map(float, [m.group(1), m.group(2), m.group(3), m.group(4)])
                                                    for old_rect, new_rect in packer.mapping.items():
                                                        if abs(cx - old_rect[0]) < 1 and abs(cy - old_rect[1]) < 1 and abs(cw - old_rect[2]) < 1 and abs(ch - old_rect[3]) < 1:
                                                            return f"Rect2( {new_rect[0]:g}, {new_rect[1]:g}, {new_rect[2]:g}, {new_rect[3]:g} )"
                                                    return m.group(0)
                                                block = re.sub(r'Rect2\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)', repl_all_rects, block)
                                            new_blocks.append(block)
                                            
                                        tscns[tscn_path] = '\n'.join(new_blocks)
                                        if tscns[tscn_path].startswith('\n['):
                                            tscns[tscn_path] = tscns[tscn_path][1:]
                                    continue
                                else:
                                    print("  Failed to repack. Falling back to scaling.")
                            
                            print("  Applying fallback scale...")
                            # Also force POT for scaled images
                            scale_factor = MAX_DIM / float(max_d)
                            new_w, new_h = int(w * scale_factor), int(h * scale_factor)
                            pot_width = next_power_of_two(new_w)
                            pot_height = next_power_of_two(new_h)
                            
                            img_resized = img.resize((pot_width, pot_height), Image.LANCZOS)
                            img_resized.save(filepath, optimize=True)
                            
                            for tscn_path in list(tscns.keys()):
                                content = tscns[tscn_path]
                                blocks = re.split(r'\n(?=\[)', content)
                                exts = get_ext_resource_paths(content)
                                target_ext_id = None
                                for k, v in exts.items():
                                    if v == res_path:
                                        target_ext_id = k
                                        break
                                
                                if not target_ext_id:
                                    continue
                                    
                                new_blocks = []
                                scaled_sub_ids = set()
                                
                                for block in blocks:
                                    if 'type="AtlasTexture"' in block or 'type="StyleBoxTexture"' in block:
                                        m_id = re.search(r'id=([A-Za-z0-9_]+)', block)
                                        if m_id and f'ExtResource( {target_ext_id} )' in block:
                                            scaled_sub_ids.add(m_id.group(1))
                                            def scale_rect(m):
                                                rx, ry, rw, rh = map(float, [m.group(1), m.group(2), m.group(3), m.group(4)])
                                                return f"Rect2( {int(rx*scale_factor)}, {int(ry*scale_factor)}, {int(rw*scale_factor)}, {int(rh*scale_factor)} )"
                                            block = re.sub(r'Rect2\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)', scale_rect, block)
                                            
                                    elif 'type="SpriteFrames"' in block:
                                        m_id = re.search(r'id=([A-Za-z0-9_]+)', block)
                                        if m_id:
                                            used_subs = re.findall(r'SubResource\(\s*([A-Za-z0-9_]+)\s*\)', block)
                                            if any(sub in scaled_sub_ids for sub in used_subs):
                                                scaled_sub_ids.add(m_id.group(1))
                                                
                                    elif block.startswith('[node'):
                                        needs_scale = False
                                        if f'texture = ExtResource( {target_ext_id} )' in block:
                                            needs_scale = True
                                        else:
                                            for sub_id in scaled_sub_ids:
                                                if f'texture = SubResource( {sub_id} )' in block or f'frames = SubResource( {sub_id} )' in block:
                                                    needs_scale = True
                                                    break
                                                    
                                        if needs_scale and 'custom_styles' not in block:
                                            multiplier = 1.0 / scale_factor
                                            m_type = re.search(r'type="([^"]+)"', block.split('\n')[0])
                                            node_type = m_type.group(1) if m_type else ""
                                            m_scale = re.search(r'\nscale\s*=\s*Vector2\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)', block)
                                            m_rect_scale = re.search(r'\nrect_scale\s*=\s*Vector2\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)', block)
                                            if m_scale:
                                                orig_x, orig_y = float(m_scale.group(1)), float(m_scale.group(2))
                                                block = re.sub(r'\nscale\s*=\s*Vector2\([^)]+\)', f'\nscale = Vector2( {orig_x*multiplier:g}, {orig_y*multiplier:g} )', block)
                                            elif m_rect_scale:
                                                orig_x, orig_y = float(m_rect_scale.group(1)), float(m_rect_scale.group(2))
                                                block = re.sub(r'\nrect_scale\s*=\s*Vector2\([^)]+\)', f'\nrect_scale = Vector2( {orig_x*multiplier:g}, {orig_y*multiplier:g} )', block)
                                            else:
                                                lines = block.split('\n')
                                                prop = "rect_scale" if node_type in ['TextureRect', 'TextureButton', 'Control', 'Panel', 'Button', 'Label'] else "scale"
                                                lines.insert(1, f"{prop} = Vector2( {multiplier:g}, {multiplier:g} )")
                                                block = '\n'.join(lines)
                                                
                                        if 'region_rect' in block and needs_scale:
                                            def scale_rect_node(m):
                                                rx, ry, rw, rh = map(float, [m.group(1), m.group(2), m.group(3), m.group(4)])
                                                return f"Rect2( {int(rx*scale_factor)}, {int(ry*scale_factor)}, {int(rw*scale_factor)}, {int(rh*scale_factor)} )"
                                            block = re.sub(r'region_rect\s*=\s*Rect2\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)', scale_rect_node, block)
                                            
                                    new_blocks.append(block)
                                    
                                tscns[tscn_path] = '\n'.join(new_blocks)
                                if tscns[tscn_path].startswith('\n['):
                                    tscns[tscn_path] = tscns[tscn_path][1:]
                except Exception as e:
                    print(f"Error processing {file}: {e}")
                    
    for path, content in tscns.items():
        save_tscn(path, content)
    print("Done!")

if __name__ == '__main__':
    process_repacking(r"C:\Users\wolff\Documents\SDKVita\The Case of the Golden Idol\SteamVersion\NewExtractPCK")
