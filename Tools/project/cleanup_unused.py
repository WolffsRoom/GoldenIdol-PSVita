# -*- coding: utf-8 -*-
# Detect (and optionally move out of the PCK) unused scenes and images.
#
# Safe because the game references every scene/image by LITERAL res:// paths
# (verified: 0 string-concatenated load() calls), so a path that appears in NO
# .gd/.tscn/.tres is genuinely unreachable.
#
# Pass 1: scenario .tscn not referenced anywhere -> unused scenes.
# Pass 2: images (.png/.jpg/.svg) whose path appears in NO remaining scene/script
#         (corpus excludes the unused scenes, so images used only by a prototype
#         scene also fall out) -> unused images.
# Moves source + .import + every .stex variant to ../UnusedAssets/ (outside the
# PCK root), preserving relative paths, with a manifest for undo.
#
#   python cleanup_unused.py            # REPORT only
#   python cleanup_unused.py --move     # actually move
import os, re, sys, shutil

def _project_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, "SteamVersion", "NewExtractPCK")):
            return d
        d = os.path.dirname(d)
    return os.getcwd()

_ROOT_DIR = _project_root()
ROOT = os.path.join(_ROOT_DIR, "SteamVersion", "NewExtractPCK")
OUT = os.path.join(_ROOT_DIR, "SteamVersion", "UnusedAssets")
IMP = os.path.join(ROOT, ".import")

def walk(exts):
    for dp, _, fns in os.walk(ROOT):
        if os.path.normpath(dp).startswith(os.path.normpath(IMP)):
            continue
        for fn in fns:
            if fn.lower().endswith(exts):
                yield os.path.join(dp, fn)

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

def build_corpus(exclude=set()):
    text = []
    # Include every text/config that can reference an asset by path, EXCEPT
    # .import (which self-references its own source). project.godot/.json/.cfg
    # matter for icons, boot splash and scenario data.
    for p in walk((".gd", ".tscn", ".tres", ".godot", ".cfg", ".json", ".txt")):
        if rel(p) in exclude:
            continue
        try:
            text.append(open(p, encoding="utf-8", errors="ignore").read())
        except Exception:
            pass
    return "\n".join(text)

def main(do_move):
    # --- Pass 1: unused scenario scenes ---
    scenes = [rel(p) for p in walk((".tscn",)) if rel(p).startswith("scenarios/")]
    corpus = build_corpus()
    unused_scenes = []
    for s in scenes:
        # reference = the path appears somewhere OTHER than its own file
        others = corpus.replace(open(os.path.join(ROOT, s), encoding="utf-8", errors="ignore").read(), "", 1)
        if s not in others:
            unused_scenes.append(s)

    # --- Pass 2: unused images (corpus excludes the unused scenes) ---
    corpus2 = build_corpus(exclude=set(unused_scenes))
    images = [rel(p) for p in walk((".png", ".jpg", ".jpeg", ".svg"))]
    unused_images = [im for im in images if im not in corpus2
                     and os.path.basename(im) not in corpus2]

    # --- report ---
    def size_of(relpath):
        return os.path.getsize(os.path.join(ROOT, relpath))
    sc_sz = sum(size_of(s) for s in unused_scenes)
    im_sz = 0
    for im in unused_images:
        im_sz += size_of(im)
        # add .stex variants
        impf = os.path.join(ROOT, im + ".import")
        if os.path.exists(impf):
            for st in re.findall(r'res://\.import/([^"\]]+)', open(impf, encoding="utf-8", errors="ignore").read()):
                fp = os.path.join(IMP, st)
                if os.path.exists(fp):
                    im_sz += os.path.getsize(fp)

    print("UNUSED SCENES: %d  (%.1f MB)" % (len(unused_scenes), sc_sz/1048576))
    print("UNUSED IMAGES: %d  (%.1f MB incl. .stex)" % (len(unused_images), im_sz/1048576))
    print("TOTAL would free from PCK: ~%.1f MB" % ((sc_sz+im_sz)/1048576))
    print("\n--- sample unused images (first 25) ---")
    for im in sorted(unused_images, key=size_of, reverse=True)[:25]:
        print("  %6.2f MB  %s" % (size_of(im)/1048576, im))

    if not do_move:
        # write full lists for review
        open(os.path.join(os.path.dirname(OUT), "unused_scenes.txt"), "w").write("\n".join(sorted(unused_scenes)))
        open(os.path.join(os.path.dirname(OUT), "unused_images.txt"), "w").write("\n".join(sorted(unused_images)))
        print("\n(REPORT only. Full lists written next to UnusedAssets/. Run with --move to apply.)")
        return

    # --- move ---
    manifest = []
    def move(relpath):
        src = os.path.join(ROOT, relpath)
        if not os.path.exists(src):
            return
        dst = os.path.join(OUT, relpath)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        manifest.append(relpath)

    for s in unused_scenes:
        move(s)
    for im in unused_images:
        impf_rel = im + ".import"
        impf = os.path.join(ROOT, impf_rel)
        stex = []
        if os.path.exists(impf):
            stex = re.findall(r'res://\.import/([^"\]]+)', open(impf, encoding="utf-8", errors="ignore").read())
        move(im)
        if os.path.exists(impf):
            move(impf_rel)
        for st in stex:
            move(".import/" + st)
    open(os.path.join(OUT, "MANIFEST.txt"), "w").write("\n".join(manifest))
    print("\nMOVED %d files to %s" % (len(manifest), OUT))

def restore():
    mani = os.path.join(OUT, "MANIFEST.txt")
    if not os.path.exists(mani):
        print("no manifest"); return
    n = 0
    for relpath in open(mani).read().split("\n"):
        relpath = relpath.strip()
        if not relpath:
            continue
        src = os.path.join(OUT, relpath)
        dst = os.path.join(ROOT, relpath)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            n += 1
    print("Restored %d files." % n)

if __name__ == "__main__":
    if "--restore" in sys.argv:
        restore()
    else:
        main("--move" in sys.argv)
