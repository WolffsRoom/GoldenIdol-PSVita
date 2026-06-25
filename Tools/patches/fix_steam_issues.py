import os

def fix_steam_issues(target_dir):
    # 1. Fix steam_dummy.gd syntax
    dummy_path = os.path.join(target_dir, "steam_dummy.gd")
    if os.path.exists(dummy_path):
        with open(dummy_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = content.replace("var user = SteamUserDummy.new()", "var user\n\nfunc _init():\n\tuser = SteamUserDummy.new()")
        
        with open(dummy_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    # 2. Fix project.godot to remove the steam_api plugin entirely
    project_path = os.path.join(target_dir, "project.godot")
    if os.path.exists(project_path):
        with open(project_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        for line in lines:
            if "res://addons/steam_api/plugin.cfg" not in line:
                new_lines.append(line)
                
        with open(project_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
if __name__ == '__main__':
    fix_steam_issues(r"C:\Users\wolff\Documents\SDKVita\The Case of the Golden Idol\SteamVersion\NewExtractPCK")
