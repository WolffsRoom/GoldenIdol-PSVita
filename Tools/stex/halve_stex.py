# -*- coding: utf-8 -*-
# Downscale an UNCOMPRESSED RGBA4444 Godot .stex by 2x in each dimension.
# Works directly on the packed 16-bit data, averaging each 4-bit channel in
# place -> packing-agnostic (no need to know the R/G/B/A nibble order).
#   python halve_stex.py <in.stex> <out.stex>
import sys, struct, numpy as np

def main(inp, outp):
    with open(inp, "rb") as f:
        blob = f.read()
    assert blob[0:4] == b"GDST", "not a .stex"
    w, h, flags, fmt = struct.unpack_from("<IIII", blob, 4)
    assert not (fmt & 0x00200000), "input is WebP, need uncompressed variant"
    assert (fmt & 0xFF) == 6, "expected FORMAT_RGBA4444 (6), got %d" % (fmt & 0xFF)
    data = np.frombuffer(blob, dtype="<u2", count=w*h, offset=20).reshape(h, w)

    w2, h2 = w // 2, h // 2
    data = data[:h2*2, :w2*2]                      # crop to even dims
    out = np.zeros((h2, w2), dtype=np.uint32)
    for shift in (0, 4, 8, 12):                    # each 4-bit channel
        ch = ((data >> shift) & 0xF).astype(np.uint16)
        blk = ch.reshape(h2, 2, w2, 2)             # 2x2 blocks
        avg = (blk.sum(axis=(1, 3)) + 2) // 4      # rounded mean
        out |= (avg.astype(np.uint32) & 0xF) << shift
    out = out.astype("<u2")

    hdr = bytearray(20)
    hdr[0:4] = b"GDST"
    struct.pack_into("<IIII", hdr, 4, w2, h2, flags, fmt)
    with open(outp, "wb") as f:
        f.write(hdr)
        f.write(out.tobytes())
    print("  %dx%d -> %dx%d  (%d -> %d bytes)"
          % (w, h, w2, h2, len(blob), 20 + out.nbytes))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
