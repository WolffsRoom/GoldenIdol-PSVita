# Tools/ - The Case of the Golden Idol (PS Vita port)

Development / build scripts for the Vita port. They are **not part of the game** -
they operate on the extracted project at `SteamVersion/NewExtractPCK` (and a few on
`game_data/`, `Trophy/`, `VPK Files/`).

The original test PC build lives in `SteamVersion/Original (SteamVersion)`; the Vita
working copy is `SteamVersion/NewExtractPCK`; assets removed from the build are parked
in `SteamVersion/UnusedAssets`.

## Running

Run from the **project root** (`The Case of the Golden Idol/`):

```
python Tools/<category>/<script>.py [args]
```

The `stex/`, `project/` and `trophy/` scripts locate the project root automatically (they
walk up from their own location). `textures/build_beach_textures.py` uses paths relative to
the current directory, so the current directory must be the project root. The rest take
explicit path arguments.

The self-contained release / distributable patcher pipeline (`build_patch.py`,
`patch_apply.py`, `patch_engine_animated.py`, `update_bat.py` + `Build_New_Patch.bat` +
`game_data/`) stays in `Release/` and is **not** moved here, because its `.bat` and data are
coupled to that folder.

## Layout

```
Tools/
  stex/        low-level .stex (StreamTexture) format operations
    fix_vram_textures.py   Repoints VRAM (mode=2) .import to the RGBA4444 .etc variant
                           so the Vita stops loading the unrenderable S3TC/ETC2 variant
                           (white/black textures). apply / --restore / optional path filter.
                           NOTE: a .import edit is reverted by the Godot editor on reload -
                           see Warning 2.
    fix_webp_stex.py       Swaps large lossless-WebP .stex (which the Vita libwebp can't
                           decode -> failed decode -> scene load crash) for their
                           uncompressed RGBA4444 .etc variant, by max-dimension threshold.
                           apply [threshold_px] / --restore.
    halve_stex.py          Downscales an uncompressed RGBA4444 .stex 2x in each dimension,
                           packing-agnostic (averages each 4-bit channel in place).
                           args: <in.stex> <out.stex>
    resize_stex.py         Fractional num/den downscale of an uncompressed RGBA4444 .stex,
                           writes flags=0 (no mipmaps). args: <in.stex> <out.stex> <num> <den>
  textures/    higher-level texture / asset optimization
    lossless_vita_optimizer.py  Main optimizer: scans for textures over Vita limits
                                (>4096px / non-POT), repacks animation frames into a
                                Power-of-Two grid, rewrites the .tscn Rect2 frame coords,
                                downscales oversized images and compensates with node scale.
    build_beach_textures.py     Rebuilds the DLC beach scene textures for CDRAM: islandmorning
                                -> dithered RGBA4444; beackanimated -> 12 full-res frames
                                packed 3x4 into a 2880x1800 RGBA4444 sheet.
    adjust_anim.py              Choreographs the custom "Ported by WolffsRoom" splash
                                animation into the boot sequence (edits main.gd).
    fix_idol_animation.py       Restores the splash_statue atlas and applies bilinear filter
                                + scale tweaks for the DLC splash. args: <orig_dir> <target_dir>
  project/     project hygiene
    cleanup_unused.py      Detects unused scenes + prototype images and moves them out of the
                           PCK to SteamVersion/UnusedAssets (manifest for undo). Reliable
                           because the game references assets by literal res:// paths.
                           (report) / --move / --restore.
    restore_imports.py     Selective import strategy: NPOT textures -> lossless (mode=0) to
                           avoid the PowerVR ETC-on-NPOT GPU crash; POT atlases kept VRAM
                           (mode=2). args: <orig_dir> <target_dir>
  vita/        Vita platform configuration
    apply_vita_settings.py        Inserts the [input_devices] / Vita-specific block into
                                  project.godot. arg: <project.godot path>
    patch_sfo_extended_memory.py  Patches PARAM.SFO memory flags (extended memory mode) for
                                  the working memory budget. arg: <param.sfo> (default param.sfo)
  patches/     GDScript / content patches
    fix_steam_issues.py    Bypasses Steam init (steam_dummy.gd + project.godot) so the game
                           boots on the Vita without the Steam DLL. arg: <target_dir>
    patch_dlcs_v2.py       Injects bypasses to unlock both DLCs locally (main.gd).
    patch_credits_v4.py    Injects the custom port splash into the boot/credits sequence.
    improvements.py        Input/control rewrites (project.godot + main.gd): hybrid pointer,
                           right-stick zoom, Select -> ui_cancel. arg: <target_dir>
  trophy/
    build_trp.py           Packs Trophy/golden_idol into an unencrypted PS Vita TROPHY.TRP
                           (the format read by Rinnegatamante's NoTrpDrm). Default source is
                           <root>/Trophy/golden_idol; or pass <folder> <out.TRP>.

  (binaries / external tools kept at Tools/ root)
    ffmpeg.exe                 Re-encode intermission videos to Theora .ogv.
    godotpcktool.exe           Pack / unpack .pck.
    Godot_v3.5-rc5-vita/       The godot-vita editor / export templates.
    GDRE_tools-.../            Godot RE tools (extract the original .pck).
    vita-crashdump-.../        Decode .psp2dmp coredumps against eboot.elf.
    PrincessLog/               Vita net logging.
    AssetStudio...zip          Asset inspection.
    README.txt                 Original narrative walkthrough of the whole port (history).
```

## Warnings / project notes

1. **.stex format and RGBA4444 packing.** The uncompressed variant the Vita renders is
   RGBA4444: header `fmt` dword `0x07000006`, pixel = `R4<<12 | G4<<8 | B4<<4 | A4`, with
   `nibble = c*15//255`. The `stex/` scripts assume the `.etc.stex` variant already exists
   (Godot generates it for VRAM-mode imports).

2. **The Godot editor reverts .import edits.** On project reload the editor regenerates the
   `.import` `[remap]` from the import params, so `fix_vram_textures.py` (which rewrites
   `[remap]`) does NOT survive a reload. The durable fix is to edit the `.stex` files
   directly (mirror the RGBA4444 `.etc.stex` over the `.s3tc.stex`/`.etc2.stex`), which the
   editor does not touch (the source PNG md5 is unchanged). Likewise, do NOT force a manual
   Reimport of `beackanimated_export2` or `islandmorning` - it regenerates them at full WebP
   resolution and brings back the DLC decode/OOM crash.

3. **CDRAM budget (~112 MB).** RGBA4444 is twice the size of the compressed VRAM variant, so
   uncompressing/mirroring ALL VRAM textures overflows CDRAM and blacks out the menu. Only
   touch the few textures that are actually broken (e.g. the DLC splash statue), or downscale
   them with `halve_stex.py` / `resize_stex.py`.

4. **Run from the project root.** `build_beach_textures.py` uses CWD-relative paths. The
   `Release/` patcher pipeline likewise expects its own folder as the working directory.
