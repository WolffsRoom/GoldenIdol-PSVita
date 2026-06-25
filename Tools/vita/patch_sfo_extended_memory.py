# -*- coding: utf-8 -*-
"""Patch Vita PARAM.SFO memory flags for Golden Idol's working memory mode.

Keeps title/trophy fields intact and changes the app attributes to match the
known-good profile from Release/OldestVersions/param.sfo:
  ATTRIBUTE       = 32768 (0x8000)
  ATTRIBUTE_MINOR = 16    (0x10)
  ATTRIBUTE2      = 12    (0x0C)
"""
import os
import shutil
import struct
import sys
import zipfile


PATCH_VALUES = {
    "ATTRIBUTE": 32768,
    "ATTRIBUTE_MINOR": 16,
    "ATTRIBUTE2": 12,
}


def parse_entries(data):
    if data[:4] != b"\x00PSF":
        raise ValueError("Invalid SFO magic")

    key_table = struct.unpack_from("<I", data, 8)[0]
    data_table = struct.unpack_from("<I", data, 12)[0]
    count = struct.unpack_from("<I", data, 16)[0]

    entries = {}
    for i in range(count):
        entry = 20 + i * 16
        key_off, fmt, length, max_len, data_off = struct.unpack_from("<HHIII", data, entry)
        key_start = key_table + key_off
        key_end = data.index(b"\x00", key_start)
        key = data[key_start:key_end].decode("ascii")
        entries[key] = {
            "entry": entry,
            "fmt": fmt,
            "length": length,
            "max_len": max_len,
            "offset": data_table + data_off,
        }
    return entries


def patch_sfo_bytes(data):
    out = bytearray(data)
    entries = parse_entries(data)

    for key, value in PATCH_VALUES.items():
        if key not in entries:
            raise ValueError("%s not found in SFO" % key)
        e = entries[key]
        if e["max_len"] != 4:
            raise ValueError("%s is not a 32-bit field" % key)
        struct.pack_into("<I", out, e["offset"], value)
        struct.pack_into("<I", out, e["entry"] + 4, 4)

    return bytes(out)


def patch_sfo_file(path):
    backup = path + ".bak"
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
    data = open(path, "rb").read()
    open(path, "wb").write(patch_sfo_bytes(data))
    print("Patched SFO: %s" % path)
    print("Backup: %s" % backup)


def patch_vpk(path):
    backup = path + ".bak"
    if not os.path.exists(backup):
        shutil.copy2(path, backup)

    tmp = path + ".tmp"
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w") as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "sce_sys/param.sfo":
                data = patch_sfo_bytes(data)
            zout.writestr(info, data)
    shutil.move(tmp, path)
    print("Patched VPK SFO: %s" % path)
    print("Backup: %s" % backup)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "param.sfo"
    lower = target.lower()
    if lower.endswith(".vpk"):
        patch_vpk(target)
    else:
        patch_sfo_file(target)
    print("Memory flags: ATTRIBUTE=32768, ATTRIBUTE_MINOR=16, ATTRIBUTE2=12")


if __name__ == "__main__":
    main()
