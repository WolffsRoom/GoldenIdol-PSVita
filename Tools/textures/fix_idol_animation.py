import os
import shutil
import re

def restore_and_fix(orig_dir, target_dir):
    png_rel = os.path.join("assets", "splash", "splash_statue_spritesheet.png")
    tscn_rel = "splash_screen_dlc.tscn"
    import_rel = png_rel + ".import"
    
    # 1. Restore the original files from ExtractPCK
    print("Restoring original PNG and TSCN...")
    shutil.copy2(os.path.join(orig_dir, png_rel), os.path.join(target_dir, png_rel))
    shutil.copy2(os.path.join(orig_dir, tscn_rel), os.path.join(target_dir, tscn_rel))
    if os.path.exists(os.path.join(orig_dir, import_rel)):
        shutil.copy2(os.path.join(orig_dir, import_rel), os.path.join(target_dir, import_rel))
        
    print("Files restored successfully.")
    
    # 2. Re-apply the Node scale adjustment to 1.0 (to make it look smaller on screen)
    print("Applying scale=1.0 to AnimatedSprite...")
    tscn_path = os.path.join(target_dir, tscn_rel)
    with open(tscn_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find the AnimatedSprite block for the Idol and scale it
    blocks = re.split(r'\n(?=\[)', content)
    new_blocks = []
    for block in blocks:
        if block.startswith('[node name="AnimatedSprite"'):
            block = re.sub(r'\nscale\s*=\s*Vector2\([^)]+\)', f'\nscale = Vector2( 1.0, 1.0 )', block)
        new_blocks.append(block)
        
    new_content = '\n'.join(new_blocks)
    if new_content.startswith('\n['):
        new_content = new_content[1:]
        
    with open(tscn_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    # 3. Apply Bilinear filtering to the .import file
    import_path = os.path.join(target_dir, import_rel)
    if os.path.exists(import_path):
        with open(import_path, 'r', encoding='utf-8') as f:
            imp = f.read()
        imp = imp.replace("flags/filter=false", "flags/filter=true")
        imp = imp.replace("compress/mode=0", "compress/mode=2")
        imp = imp.replace("compress/mode=1", "compress/mode=2")
        with open(import_path, 'w', encoding='utf-8') as f:
            f.write(imp)
            
    print("Fixes applied. Now you need to run lossless_vita_optimizer.py on this file!")

if __name__ == '__main__':
    orig = r"C:\Users\wolff\Documents\SDKVita\The Case of the Golden Idol\SteamVersion\ExtractPCK"
    target = r"C:\Users\wolff\Documents\SDKVita\The Case of the Golden Idol\SteamVersion\NewExtractPCK"
    restore_and_fix(orig, target)
