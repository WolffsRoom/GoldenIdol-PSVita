# -*- coding: utf-8 -*-
# Fractional (num/den) downscale of an uncompressed RGBA4444 Godot .stex.
# Packing-agnostic: works per 4-bit channel by repeating each axis `num` times
# then box-averaging `den`x`den` blocks. Output dims must be integer.
# Output is written with flags=0 (no mipmaps) to save CDRAM/VRAM.
#   python resize_stex.py <in.stex> <out.stex> <num> <den>
import sys, struct, numpy as np

def main(inp, outp, num, den):
    blob = open(inp, "rb").read()
    assert blob[0:4] == b"GDST"
    w, h, flags, fmt = struct.unpack_from("<IIII", blob, 4)
    assert not (fmt & 0x00200000), "input is WebP; use the uncompressed variant"
    assert (fmt & 0xFF) == 6, "expected RGBA4444 (6)"
    assert (w*num) % den == 0 and (h*num) % den == 0, "non-integer output dims"
    w2, h2 = w*num//den, h*num//den
    data = np.frombuffer(blob, dtype="<u2", count=w*h, offset=20).reshape(h, w)

    out = np.zeros((h2, w2), dtype=np.uint32)
    for shift in (0, 4, 8, 12):
        ch = ((data >> shift) & 0xF).astype(np.float32)
        up = np.repeat(np.repeat(ch, num, axis=0), num, axis=1)      # h*num x w*num
        blk = up.reshape(h2, den, w2, den)
        avg = np.rint(blk.mean(axis=(1, 3))).astype(np.uint32)
        out |= (avg & 0xF) << shift
    out = out.astype("<u2")

    hdr = bytearray(20)
    hdr[0:4] = b"GDST"
    struct.pack_into("<IIII", hdr, 4, w2, h2, 0, fmt)              # flags=0
    with open(outp, "wb") as f:
        f.write(hdr); f.write(out.tobytes())
    print("  %dx%d -> %dx%d (x%d/%d)  %d -> %d bytes  flags=0"
          % (w, h, w2, h2, num, den, len(blob), 20 + out.nbytes))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
