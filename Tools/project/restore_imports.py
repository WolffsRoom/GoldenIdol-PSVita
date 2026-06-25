import os
import shutil
from PIL import Image

def is_pot(x):
    return x > 0 and (x & (x - 1)) == 0

def restore_and_fix(orig_dir, target_dir):
    # 1. Restore all .import files from orig_dir to target_dir
    print("Restoring original .import files...")
    count_restored = 0
    for root, dirs, files in os.walk(orig_dir):
        for file in files:
            if file.endswith('.import'):
                orig_path = os.path.join(root, file)
                rel_path = os.path.relpath(orig_path, orig_dir)
                target_path = os.path.join(target_dir, rel_path)
                if os.path.exists(target_path):
                    shutil.copy2(orig_path, target_path)
                    count_restored += 1
    print(f"Restored {count_restored} .import files.")

    # 2. Fix compress/mode for large POT textures
    print("Applying VRAM compression ONLY to POT textures...")
    count_vram = 0
    count_lossless = 0
    
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith('.png'):
                png_path = os.path.join(root, file)
                import_path = png_path + '.import'
                
                if os.path.exists(import_path):
                    try:
                        with Image.open(png_path) as img:
                            w, h = img.size
                            
                        # Vita GLES2 ETC1 compression ONLY supports Power of Two (POT) dimensions.
                        # NPOT textures will crash the GPU driver (C2-12828-1).
                        if is_pot(w) and is_pot(h):
                            # It's a POT texture. Safe for VRAM compression!
                            # Let's apply VRAM compression to save memory.
                            with open(import_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            if 'compress/mode=0' in content or 'compress/mode=1' in content:
                                content = content.replace('compress/mode=0', 'compress/mode=2')
                                content = content.replace('compress/mode=1', 'compress/mode=2')
                                with open(import_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                count_vram += 1
                        else:
                            # It's an NPOT texture. MUST be Lossless (0) to prevent GPU crash!
                            with open(import_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            if 'compress/mode=2' in content:
                                content = content.replace('compress/mode=2', 'compress/mode=0')
                                with open(import_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                count_lossless += 1
                                
                    except Exception as e:
                        print(f"Error processing {png_path}: {e}")
                        
    print(f"Set VRAM compression for {count_vram} POT textures.")
    print(f"Forced Lossless for {count_lossless} NPOT textures to prevent crashes.")

if __name__ == '__main__':
    orig = r"C:\Users\wolff\Documents\SDKVita\The Case of the Golden Idol\SteamVersion\ExtractPCK"
    target = r"C:\Users\wolff\Documents\SDKVita\The Case of the Golden Idol\SteamVersion\NewExtractPCK"
    restore_and_fix(orig, target)
