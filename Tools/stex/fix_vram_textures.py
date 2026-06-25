# -*- coding: utf-8 -*-
# VRAM-compressed (compress/mode=2) textures ship S3TC + ETC2 + ETC variants.
# On the Vita (PowerVR/GLES2) Godot picks the S3TC or ETC2 variant, which the
# GPU can't render with alpha -> the texture shows white/black AND the driver
# chokes (the DLC splash dropped to ~5 FPS). The ".etc" variant, however, is
# plain uncompressed RGBA4444 (fmt 0x..06) which the Vita renders fine.
#
# Fix: rewrite each such .import so the [remap] points unconditionally at the
# .etc (RGBA4444) variant, instead of letting Godot pick a compressed one.
#   python fix_vram_textures.py            (apply)
#   python fix_vram_textures.py --restore  (undo from .vrambak)
import os, sys, glob, struct

def _project_root():
    # Walk up from this file (now under Tools/<cat>/) until the project root.
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, "SteamVersion", "NewExtractPCK")):
            return d
        d = os.path.dirname(d)
    return os.getcwd()

ROOT = os.path.join(_project_root(), "SteamVersion", "NewExtractPCK")
IMP = os.path.join(ROOT, ".import")


def is_rgba4444(stex_abs):
    try:
        b = open(stex_abs, "rb").read(20)
    except IOError:
        return False
    if b[0:4] != b"GDST":
        return False
    fmt = struct.unpack_from("<I", b, 16)[0]
    return (fmt & 0xFF) == 6 and not (fmt & 0x00200000)


def restore():
    n = 0
    for bak in glob.glob(os.path.join(ROOT, "**", "*.import.vrambak"), recursive=True):
        dst = bak[:-len(".vrambak")]
        open(dst, "w", encoding="utf-8").write(open(bak, encoding="utf-8").read())
        os.remove(bak)
        n += 1
    print("Restored %d .import file(s)." % n)


def apply(path_filter=None):
    fixed = skipped = 0
    for imp in glob.glob(os.path.join(ROOT, "**", "*.import"), recursive=True):
        if path_filter and path_filter.lower() not in imp.replace("\\", "/").lower():
            continue
        txt = open(imp, encoding="utf-8").read()
        if "compress/mode=2" not in txt:
            continue
        lines = txt.split("\n")
        etc_res = None
        for ln in lines:
            if ln.startswith("path.etc="):
                etc_res = ln.split("=", 1)[1].strip().strip('"')
                break
        if etc_res is None:
            print("  SKIP (no .etc variant): %s" % os.path.basename(imp)); skipped += 1; continue
        etc_abs = os.path.join(IMP, etc_res.replace("res://.import/", ""))
        if not is_rgba4444(etc_abs):
            print("  SKIP (.etc not RGBA4444): %s" % os.path.basename(imp)); skipped += 1; continue

        out = []
        remap = False
        for ln in lines:
            s = ln.strip()
            if s == "[remap]":
                remap = True
                out.append(ln); continue
            if s.startswith("["):
                remap = False
            if remap and (ln.startswith("path.s3tc=") or ln.startswith("path.etc2=")):
                continue  # drop compressed-variant remaps
            if remap and ln.startswith("path.etc="):
                out.append('path="%s"' % etc_res)  # single unconditional path
                continue
            if ln.strip().startswith('"imported_formats"'):
                out.append('"imported_formats": [ "etc" ],'); continue
            if ln.strip().startswith('"vram_texture"'):
                out.append('"vram_texture": false'); continue
            if ln.startswith("dest_files="):
                out.append('dest_files=[ "%s" ]' % etc_res); continue
            out.append(ln)

        if not os.path.exists(imp + ".vrambak"):
            open(imp + ".vrambak", "w", encoding="utf-8").write(txt)
        open(imp, "w", encoding="utf-8").write("\n".join(out))
        fixed += 1
    print("---\nRepointed %d VRAM texture(s) to their RGBA4444 .etc variant. "
          "Skipped %d." % (fixed, skipped))


if __name__ == "__main__":
    if "--restore" in sys.argv:
        restore()
    else:
        # optional path substring filter, e.g. "splash" to only touch those
        flt = None
        for a in sys.argv[1:]:
            if not a.startswith("--"):
                flt = a
        apply(flt)
