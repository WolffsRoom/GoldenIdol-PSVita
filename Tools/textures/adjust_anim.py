import os

def adjust_animation(target_dir):
    main_gd_path = os.path.join(target_dir, "main.gd")
    with open(main_gd_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_block = """	# Load splash screen behind it
	show_splash_screen()
	
	# Fade Out (now splash screen is already loaded and music starts, but visually obscured by our fading layer)
	tween.interpolate_property(custom, "modulate", Color(1, 1, 1, 1), Color(1, 1, 1, 0), 1.5, Tween.TRANS_LINEAR, Tween.EASE_IN_OUT)
	tween.start()
	yield(tween, "tween_completed")
	
	canvas.queue_free()"""

    new_block = """	# Fade Out to black first
	tween.interpolate_property(custom, "modulate", Color(1, 1, 1, 1), Color(1, 1, 1, 0), 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN_OUT)
	tween.start()
	yield(tween, "tween_completed")
	
	yield(get_tree().create_timer(0.5), "timeout")
	canvas.queue_free()
	
	# Load splash screen AFTER fading to black
	show_splash_screen()"""

    content = content.replace(old_block, new_block)
    
    with open(main_gd_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Animation adjusted successfully!")

if __name__ == '__main__':
    adjust_animation(r"C:\Users\wolff\Documents\SDKVita\The Case of the Golden Idol\SteamVersion\NewExtractPCK")
