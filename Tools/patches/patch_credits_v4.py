import os

def patch_credits(target_dir):
    main_gd_path = os.path.join(target_dir, "main.gd")
    if os.path.exists(main_gd_path):
        with open(main_gd_path, 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        # Remove old custom_splash function
        if "func show_custom_splash():" in main_content:
            main_content = main_content[:main_content.find("func show_custom_splash():")]
            
        custom_func = """
func show_custom_splash():
	var canvas = CanvasLayer.new()
	canvas.layer = 100
	
	var custom = Control.new()
	var bg = ColorRect.new()
	bg.color = Color(0.133333, 0.12549, 0.203922, 1)
	bg.rect_min_size = Vector2(1920, 1080)
	custom.add_child(bg)
	
	var label = Label.new()
	label.text = "Port to PSVita by"
	var dynamic_font = DynamicFont.new()
	dynamic_font.font_data = load("res://assets/fonts/titlefont.tres")
	dynamic_font.size = 56
	dynamic_font.outline_color = Color(0.85098, 0.627451, 0.4, 1)
	dynamic_font.extra_spacing_char = 3
	label.add_font_override("font", dynamic_font)
	label.align = Label.ALIGN_CENTER
	label.rect_min_size = Vector2(1920, 100)
	label.rect_position = Vector2(0, 121)
	custom.add_child(label)
	
	var tex = load("res://assets/splash/LogoWolffsRoom.png")
	var tex_rect = TextureRect.new()
	tex_rect.texture = tex
	tex_rect.expand = true
	tex_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	tex_rect.rect_min_size = Vector2(1920, 800)
	tex_rect.rect_position = Vector2(0, 200)
	custom.add_child(tex_rect)
	
	var tween = Tween.new()
	custom.add_child(tween)
	
	custom.modulate = Color(1, 1, 1, 0)
	canvas.add_child(custom)
	add_child(canvas)
	
	# Fade In
	tween.interpolate_property(custom, "modulate", Color(1, 1, 1, 0), Color(1, 1, 1, 1), 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN_OUT)
	tween.start()
	yield(tween, "tween_completed")
	
	# Wait
	yield(get_tree().create_timer(1.5), "timeout")
	
	# Load splash screen behind it
	show_splash_screen()
	
	# Fade Out (now splash screen is already loaded and music starts, but visually obscured by our fading layer)
	tween.interpolate_property(custom, "modulate", Color(1, 1, 1, 1), Color(1, 1, 1, 0), 1.5, Tween.TRANS_LINEAR, Tween.EASE_IN_OUT)
	tween.start()
	yield(tween, "tween_completed")
	
	canvas.queue_free()
"""
        main_content += custom_func
        with open(main_gd_path, 'w', encoding='utf-8') as f:
            f.write(main_content)
        print("Patched main.gd with LogoWolffsRoom (with Crossfade animation)")

if __name__ == '__main__':
    patch_credits(r"C:\Users\wolff\Documents\SDKVita\The Case of the Golden Idol\SteamVersion\NewExtractPCK")
