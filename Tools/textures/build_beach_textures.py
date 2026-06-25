# -*- coding: utf-8 -*-
# Beach scene CDRAM optimization:
#  A) islandmorning -> 1920x900 RGBA4444 with ordered (Bayer 4x4) dithering
#     (halves CDRAM 6.6->3.3MB; dithering hides sky banding).
#  B) beackanimated  -> 12 of 17 frames at FULL 960x450 res, packed 3x4 into a
#     2880x1800 RGBA4444 sheet (full per-frame res => 1:1 sharp on screen).
# RGBA4444 packing (reverse-engineered): v = R4<<12|G4<<8|B4<<4|A4, nibble=c*15//255.
import struct, numpy as np
from PIL import Image

IMP = "SteamVersion/NewExtractPCK/.import/"
ASSET = "SteamVersion/NewExtractPCK/scenarios/dlc/14_mystery_of_monkey_paw_island/assets/backgrounds/"

def write_stex(path, w, h, u16):
    hdr = bytearray(20); hdr[0:4] = b"GDST"
    struct.pack_into("<IIII", hdr, 4, w, h, 0, 0x07000006)   # flags=0, RGBA4444
    open(path, "wb").write(bytes(hdr) + u16.astype("<u2").tobytes())
    print("  wrote %s  %dx%d  %d bytes" % (path.split("/")[-1], w, h, 20 + u16.size*2))

def pack4444(rgba):                       # rgba: HxWx4 uint8 -> HxW uint16
    n = (rgba.astype(np.uint16) * 15) // 255
    return (n[...,0] << 12) | (n[...,1] << 8) | (n[...,2] << 4) | n[...,3]

# ---- A) islandmorning, dithered ----
BAYER = np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]], np.float32)
def dither4(ch, x0=0, y0=0):              # ch float HxW in 0..255 -> 4-bit nibble 0..15
    h, w = ch.shape
    d = (np.tile(BAYER, (h//4+1, w//4+1))[:h, :w] / 16.0 - 0.5)   # -0.5..~0.44
    n = np.floor(ch * 15.0 / 255.0 + d + 0.5)
    return np.clip(n, 0, 15).astype(np.uint16)

im = Image.open(ASSET + "islandmorning.png").convert("RGBA")
assert im.size == (1920, 900)
a = np.asarray(im).astype(np.float32)
R = dither4(a[...,0]); G = dither4(a[...,1]); B = dither4(a[...,2])
A = (a[...,3].astype(np.uint16) * 15) // 255
island = (R << 12) | (G << 8) | (B << 4) | A
write_stex(IMP + "islandmorning.png-7bc6b304df7e861f7ef2dc9194ca3c34.stex", 1920, 900, island)

# ---- B) beackanimated 12-frame full-res sheet ----
src = open(IMP + "beackanimated_export2.png-8ae1298fcc9b1c44427d34785d072891.etc.stex", "rb").read()
sw, sh = 2880, 2700
sheet = np.frombuffer(src, "<u2", count=sw*sh, offset=20).reshape(sh, sw)
FW, FH = 960, 450
selected = [0,1,3,4,6,7,8,10,11,13,14,16]          # 12 of 17, evenly spaced
NW, NH = 2880, 1800                                 # 3 cols x 4 rows
out = np.zeros((NH, NW), np.uint16)
for j, i in enumerate(selected):
    sr, sc = i // 3, i % 3
    dr, dc = j // 3, j % 3
    out[dr*FH:(dr+1)*FH, dc*FW:(dc+1)*FW] = sheet[sr*FH:(sr+1)*FH, sc*FW:(sc+1)*FW]
write_stex(IMP + "beackanimated_export2.png-8ae1298fcc9b1c44427d34785d072891.stex", NW, NH, out)
print("selected frames:", selected)
