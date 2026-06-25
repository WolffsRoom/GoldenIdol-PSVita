# -*- coding: utf-8 -*-
# Vita fix: the engine's libwebp fails to decode LARGE lossless-WebP .stex
# textures (needs a big temp RGBA buffer that the memory-starved Vita can't
# allocate -> "Failed decoding WebP image" -> scene fails to load).
#
# Godot already generated an uncompressed RGBA4444 variant alongside each one
# (the *.etc.stex). That variant needs NO decode at all, so it loads fine AND
# uses less peak runtime memory. This script swaps the plain WebP .stex for the
# uncompressed variant, but ONLY for textures whose largest dimension exceeds a
# threshold (small WebP textures decode fine and don't need swapping).
#
#   python fix_webp_stex.py [threshold_px]   (default 2048; use 0 to do all)
#   python fix_webp_stex.py --restore        (undo: restore .webp_bak backups)
import os, sys, struct, glob

def _project_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, "SteamVersion", "NewExtractPCK")):
            return d
        d = os.path.dirname(d)
    return os.getcwd()

IMPORT_DIR = os.path.join(
    _project_root(), "SteamVersion", "NewExtractPCK", ".import")

VARIANTS = (".etc.stex", ".etc2.stex", ".s3tc.stex", ".pvrtc.stex")

def is_variant(name):
    return any(name.endswith(v) for v in VARIANTS)

def read_header(path):
    with open(path, "rb") as f:
        head = f.read(20)
    if len(head) < 20 or head[0:4] != b"GDST":
        return None
    w, h, flags, fmt = struct.unpack_from("<IIII", head, 4)
    return w, h, flags, fmt

def is_webp(fmt):       # FORMAT_BIT_WEBP = 0x00200000
    return bool(fmt & 0x00200000)

def restore():
    n = 0
    for bak in glob.glob(os.path.join(IMPORT_DIR, "*.stex.webp_bak")):
        orig = bak[:-len(".webp_bak")]
        with open(bak, "rb") as s, open(orig, "wb") as d:
            d.write(s.read())
        os.remove(bak)
        n += 1
        print("  restored", os.path.basename(orig))
    print("Restored %d file(s)." % n)

def fix(threshold):
    swapped = saved_mb = added_mb = 0
    for path in sorted(glob.glob(os.path.join(IMPORT_DIR, "*.stex"))):
        name = os.path.basename(path)
        if is_variant(name):
            continue
        hdr = read_header(path)
        if not hdr or not is_webp(hdr[3]):
            continue
        w, h = hdr[0], hdr[1]
        if max(w, h) <= threshold:
            continue
        # find an uncompressed variant to copy from
        base = path[:-len(".stex")]
        src = None
        for v in VARIANTS:
            cand = base + v
            if os.path.exists(cand):
                vh = read_header(cand)
                if vh and not is_webp(vh[3]):   # must itself be uncompressed
                    src = cand
                    break
        if not src:
            print("  SKIP (no uncompressed variant): %s  %dx%d" % (name, w, h))
            continue
        bak = path + ".webp_bak"
        if not os.path.exists(bak):
            os.rename(path, bak)
        else:
            os.remove(path)
        with open(src, "rb") as s, open(path, "wb") as d:
            d.write(s.read())
        old = os.path.getsize(bak)
        new = os.path.getsize(path)
        swapped += 1
        added_mb += (new - old) / 1048576.0
        print("  FIXED %s  %dx%d  (%s, %.1fMB -> %.1fMB)"
              % (name, w, h, os.path.basename(src), old/1048576.0, new/1048576.0))
    print("---")
    print("Swapped %d texture(s). PCK grows ~%.1f MB on disk "
          "(runtime memory unchanged or lower)." % (swapped, added_mb))

if __name__ == "__main__":
    if "--restore" in sys.argv:
        restore()
    else:
        th = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 2048
        print("Swapping WebP .stex with max dimension > %d px ..." % th)
        fix(th)
