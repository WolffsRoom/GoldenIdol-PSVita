import os

def patch_dlcs(target_dir):
    main_gd_path = os.path.join(target_dir, "main.gd")
    if os.path.exists(main_gd_path):
        with open(main_gd_path, 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        # Force DLC variables to always be true
        if "var dlc1_available = false" in main_content:
            main_content = main_content.replace(
                "var dlc1_available = false",
                "var dlc1_available = true"
            )
        
        if "var dlc2_available = false" in main_content:
            main_content = main_content.replace(
                "var dlc2_available = false",
                "var dlc2_available = true"
            )
            
        # Bypass the directory check entirely
        if "var dlc1_file_exists = dir.file_exists" in main_content:
            main_content = main_content.replace(
                "var dlc1_file_exists = dir.file_exists(OS.get_executable_path().get_base_dir() + \"/dlc.txt\")",
                "var dlc1_file_exists = true"
            )
            
        if "var dlc2_file_exists = dir.file_exists" in main_content:
            main_content = main_content.replace(
                "var dlc2_file_exists = dir.file_exists(OS.get_executable_path().get_base_dir() + \"/dlc2.txt\")",
                "var dlc2_file_exists = true"
            )

        with open(main_gd_path, 'w', encoding='utf-8') as f:
            f.write(main_content)
        
        print("DLCs permanently forced to ON in main.gd")

if __name__ == '__main__':
    patch_dlcs(r"C:\Users\wolff\Documents\SDKVita\The Case of the Golden Idol\SteamVersion\NewExtractPCK")
