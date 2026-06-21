<p align="center">
  <img src="GoldenIdonVita.png" alt="The Case of the Golden Idol - PS Vita Port">
</p>

# The Case of the Golden Idol - PS Vita Port

A port of **The Case of the Golden Idol** for the PlayStation Vita, adapted from the original Godot Engine PC release. This repository contains the source scripts, patching engines, and tools created to adapt the game to run natively on the PS Vita hardware.

## Installation

1. Head to the **[Releases](../../releases)** tab.
2. Download the latest `GoldenIdol-Patch.zip` and `GoldenIdol-Vita-x.x.x.vpk`.
3. Extract `GoldenIdol-Patch.zip` into a new folder on your PC.

### HOW TO APPLY THE PATCH:
1. Open Steam, right-click on "The Case of the Golden Idol", go to **Manage -> Browse local files**.
2. Copy the file named `game.pck` from that folder.
3. Paste the `game.pck` file **EXACTLY INTO THE `DataSteam` FOLDER** of your extracted patcher.
4. Go back to the main patcher folder and run `ApplyPatch.bat`. Follow the on-screen instructions to select your language.
5. Wait for the process to finish. It will automatically apply the patch and create a new folder named `game_data` containing your patched game file.
6. Install the `GoldenIdol-Vita-X.X.X.vpk` on your PS Vita using VitaShell or **[FMVita](https://github.com/WolffsRoom/FMVita)** (my personalized VitaShell).
7. Connect your Vita via FTP or USB, and copy the entire newly created `game_data` folder into your Vita's game app folder at:
   `ux0:app/IDOL00001/`
   *(This ensures the file ends up exactly at `ux0:app/IDOL00001/game_data/game.pck`, not just the root app folder).*
8. Have fun!

> **⚠️ Note**: You MUST own the original game on Steam to generate the Vita playable files. No game assets are provided in this repository.

> **UPDATE WARNING**: IF YOU WANT TO UPDATE THE GAME, UPDATE THE GAME FILES TOO, NOT JUST VPK

---

## Controls (Controles)

<p align="center">
  <img src="controlsvita.png" alt="PS Vita Controls" width="70%">
</p>

- **D-Pad Up/Down**: Zoom In / Zoom Out
- **D-Pad Left**: Show/Hide highlights
- **Joystick Right:** Move in zoom
- **Joystick Left:** Mouse control
- **Touch Screen**: Interact (click)
- **Cross (X)**: Confirm / Interact
- **Circle (O)**: Cancel / Back
- **Triangle / Square**: Open Thinking Panel
- **Select:** Options

---

## Screenshots

<p align="center">
  <img src="Prints/2026-06-04-162650-948987.png" width="48%">
  <img src="Prints/2026-06-04-162656-152818.png" width="48%">
  <img src="Prints/2026-06-04-162711-784811.png" width="48%">
  <img src="Prints/2026-06-04-162738-077905.png" width="48%">
  <img src="Prints/2026-06-04-162740-162957.png" width="48%">
  <img src="Prints/2026-06-04-162748-788421.png" width="48%">
</p>

---

## Main Tools Used

This port was made possible thanks to the following incredible tools:

### **GDRE_Tools**
- **Purpose**: Used to extract the original PCK from the Steam version, allowing the project to be reconstructed and opened in the Godot Engine.
- **Source**: [https://github.com/GDRETools/gdsdecomp](https://github.com/GDRETools/gdsdecomp)

### **GODOT PSVita**
- **Purpose**: Used to compile the final `.vpk` for the Vita, and modify essential game files to improve the interface and adapt playability for the console.
- **Source**: [https://github.com/SonicMastr/godot-vita](https://github.com/SonicMastr/godot-vita)

### **AssetStudio**
- **Purpose**: Used to explore the files of the Unity version of the game (REDUX version), with the main goal of creating a tool to migrate the newly translated languages back to the Godot version.
- **Note**: The translation project is still a work-in-progress, I currently adding accentuation support to the TTF fonts used by the game.
- **Source**: [https://github.com/Perfare/AssetStudio](https://github.com/Perfare/AssetStudio)

---

## Python Automation Tools

A series of `.py` tools were created to help automate the massive series of adjustments needed to make the PC assets run natively on the PS Vita constraints. These can be found in the `Tools.zip` or the source tree:

| Tool Script | Usage / Purpose |
| :--- | :--- |
| `lossless_vita_optimizer.py` | Automatically optimizes large textures for PS Vita's VRAM constraints without visible quality loss. |
| `restore_imports.py` | Restores corrupted or missing `.import` configuration files after the original PCK extraction. |
| `apply_vita_settings.py` | Automatically forces necessary PS Vita target settings directly into the `project.godot` file. |
| `patch_dlcs_v2.py` | Integrates and patches the DLCs (*Spider of Lanka* & *Lemurian Vampire*) for console compatibility. |
| `patch_credits_v4.py` | Adjusts and adapts the ending credits UI constraints to match the Vita's native resolution. |
| `fix_idol_animation.py` | Tweaks memory-heavy animation loops so they run flawlessly and smoothly on Vita memory. |
| `adjust_anim.py` | Recalculates screen bounds and positional anchors for game elements during animations. |
| `improvements.py` | Applies overall UI/UX improvements, specifically adapting pointer and text elements. |
| `fix_steam_issues.py` | Removes Steamworks dependencies and PC-specific API calls that would crash the console runtime. |
| `patch_engine_animated.py` | Custom multi-threaded patching engine built with `bsdiff4` to generate the final user patch. |

---

## PS Vita Improvements

Since this port is based on the Godot version, I took the liberty (as it was easy) of reworking several parts of the game to make it feel native on the console:

- **Touch-optimized screens:** Rework in some screens, such as the main menu (`splash_screen_dlc`), to be optimized for the touch screen.
- **New controls image:** Redesigned the controls help image specifically for the PS Vita.
- **Screen-opening animations:** Improved and added animations to the opening of menus and dialogs.
- **Mouse support:** Developed a virtual cursor/mouse system driven by the analog stick.
- **Reworked controls:** Replaced the original Xbox-style control scheme to make better use of the PS Vita's buttons.

---

## Planned Improvements
- **v0.8.0**
  - Put trophy support.
  - Set a performance improvements during scenario transitions.
- **v0.9.0**
  - Put support for the OST DLC.
- **v1.0.0**
  - Put language switching in the patcher for the generated PCK, using data from the Unity version.

---

## Known Issues
- Just a slightly longer loading time for screens and levels, nothing serious (about 5 seconds).

---

## IA Notice

This project utilized **Gemini 3.1 Pro** through the **Antigravity IDE** to optimize the creation of the Python scripts, compile differential patchers, and automate the extensive pipeline needed to port the *Golden Idol* Godot project to the PS Vita.

---

Follow my other work here as well:
[https://wolffsroom.wordpress.com/](https://wolffsroom.wordpress.com/)
