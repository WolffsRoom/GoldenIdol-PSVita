import os

def apply_vita_settings(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # We need to insert [input_devices]
    # And modify [rendering] variables

    # Let's just append to the end, Godot parser handles duplicates by taking the last value
    # Or we can just append safely
    
    append_str = """
[input_devices]

pointing/emulate_mouse_from_touch=true

[rendering]

quality/driver/driver_name="GLES2"
quality/driver/fallback_to_gles2=true
vram_compression/import_etc=true
vram_compression/import_s3tc=false
"""

    lines.append(append_str)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    print("Vita settings appended to project.godot")

if __name__ == '__main__':
    apply_vita_settings('project.godot')
