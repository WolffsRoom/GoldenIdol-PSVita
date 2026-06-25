import os

def apply_improvements(target_dir):
    # 1. Update project.godot to map Select (10) to ui_cancel
    project_path = os.path.join(target_dir, "project.godot")
    with open(project_path, 'r', encoding='utf-8') as f:
        proj_content = f.read()
    
    old_cancel = 'ui_cancel={\n"deadzone": 0.5,\n"events": [ Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"alt":false,"shift":false,"control":false,"meta":false,"command":false,"pressed":false,"scancode":16777220,"physical_scancode":0,"unicode":0,"echo":false,"script":null)\n, Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":1,"pressure":0.0,"pressed":false,"script":null)\n ]\n}'
    
    new_cancel = 'ui_cancel={\n"deadzone": 0.5,\n"events": [ Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"alt":false,"shift":false,"control":false,"meta":false,"command":false,"pressed":false,"scancode":16777220,"physical_scancode":0,"unicode":0,"echo":false,"script":null)\n, Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":1,"pressure":0.0,"pressed":false,"script":null)\n, Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":10,"pressure":0.0,"pressed":false,"script":null)\n ]\n}'
    
    proj_content = proj_content.replace(old_cancel, new_cancel)
    with open(project_path, 'w', encoding='utf-8') as f:
        f.write(proj_content)

    # 2. Update main.gd for pointer visibility and right thumbstick zoom
    main_gd = os.path.join(target_dir, "main.gd")
    with open(main_gd, 'r', encoding='utf-8') as f:
        main_content = f.read()

    # Update Right Thumbstick Zoom
    old_dpad_up = 'if event.is_action_pressed("dpad_up"):'
    new_dpad_up = 'if event.is_action_pressed("dpad_up") or event.is_action_pressed("right_thumbstick_up"):'
    main_content = main_content.replace(old_dpad_up, new_dpad_up)

    old_dpad_down = 'if event.is_action_pressed("dpad_down"):'
    new_dpad_down = 'if event.is_action_pressed("dpad_down") or event.is_action_pressed("right_thumbstick_down"):'
    main_content = main_content.replace(old_dpad_down, new_dpad_down)

    # Update Pointer Visibility on Joypad Motion (Left Stick)
    old_warp = 'get_viewport().warp_mouse(get_viewport().get_mouse_position() + movement)'
    new_warp = 'get_viewport().warp_mouse(get_viewport().get_mouse_position() + movement)\n\t\tpointer.modulate.a = 1.0'
    main_content = main_content.replace(old_warp, new_warp)

    # Update Pointer Visibility on Touch
    old_mouse_button = 'elif event is InputEventMouseButton:'
    new_mouse_button = 'elif event is InputEventScreenTouch or event is InputEventScreenDrag:\n\t\tpointer.modulate.a = 0.0\n\n\telif event is InputEventMouseButton:'
    main_content = main_content.replace(old_mouse_button, new_mouse_button)
    
    with open(main_gd, 'w', encoding='utf-8') as f:
        f.write(main_content)

    print("Improvements applied!")

if __name__ == '__main__':
    apply_improvements(r"C:\Users\wolff\Documents\SDKVita\The Case of the Golden Idol\SteamVersion\NewExtractPCK")
