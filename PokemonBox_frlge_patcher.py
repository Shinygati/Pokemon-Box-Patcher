#!/usr/bin/env python3
"""
Pokemon Box: Ruby & Sapphire (USA GPXE01 / PAL GPXP01) - FireRed / LeafGreen / Emerald Adventure Mode patcher

This script contains ONLY patch data (file offsets + new bytes written for this mod).
It contains no game code, disc files, ROMs or BIOS. You must supply your own:
  * Pokemon Box Ruby & Sapphire ISO dumped from your own disc:
      USA: untouched, or with the "Universal Version" patch (windyprairie, Project Pokemon) applied
      PAL: untouched
  * Optional: FireRed / LeafGreen / Emerald ROMs dumped from your own cartridges
      USA disc: English (BPRE / BPGE / BPEE)
      PAL disc: English, French, Italian, German or Spanish

It reads Start.dol and gbarom.arc from your ISO, patches them, adds the ROMs as files and
writes a new ISO with a rebuilt file table. Your original ISO is never modified.
Also includes the Universal Version's Box changes (withdraw without 100 Pokedex entries,
no story-progress restriction; USA: any-language Ruby/Sapphire), credit to windyprairie.

Usage:
  Double-click this file (or run "py box_frlg_e_patcher.py") and answer the questions.
  Command-line use also works:
  py box_frlg_e_patcher.py BOX.iso OUT.iso [--firered FR.gba] [--leafgreen LG.gba] [--emerald E.gba]

Requires Python 3.8+ only (no extra packages).
"""
import sys, os, struct, hashlib, argparse

# Per disc: DOL_PATCH entries are (offset, new bytes, sha1-16 of the original bytes [, ... of a
# Universal-patched disc]); arcs are (kind, [(offset, new bytes, sha1-16 of original)], sha1 of result)
REGIONS = {'GPXE01': {'name': 'USA', 'langs': 'E', 'bneed_off': 1455660, 'dol': [(117092, '48146811', 'fabba5cfed994bdb', 'fabba5cfed994bdb'), (118088, '4814642d', 'fabba5cfed994bdb', 'fabba5cfed994bdb'), (119375, '00', '3c363836cf4e1666', '5ba93c9db0cff93f'), (157564, '4813cf65', 'a02a42acd7d59781', 'a02a42acd7d59781'), (157732, '4813cf05', '306e25d73fb33c5e', '306e25d73fb33c5e'), (157748, '4813cef5', '306e25d73fb33c5e', '306e25d73fb33c5e'), (159053, '7f', 'fb3c6e4de85bd9ea', 'fb3c6e4de85bd9ea'), (159085, '7f', 'fb3c6e4de85bd9ea', 'fb3c6e4de85bd9ea'), (177704, '3ca00200', '161a4b9807dfb7b1', 'e1b9ec6ec5da1f6b'), (179984, '3800000028000000', 'c9f85163901b5b58', 'd510e71de75348c5'), (184284, '481360a54800003c', 'c9f85163901b5b58', '056599ea01793e89'), (184604, '48136525', 'e473111812cfa85a', 'e473111812cfa85a'), (184616, '4813654148136565', '2d25bf6663c0ed31', '2d25bf6663c0ed31'), (195252, '4813369d', 'd6e5ab6356b71033', 'd6e5ab6356b71033'), (236899, '00', 'a42c6cf1de3abfde', '5ba93c9db0cff93f'), (236927, '00', '3c363836cf4e1666', '5ba93c9db0cff93f'), (535812, '480e048d', '97c466a85370425c', '97c466a85370425c'), (536848, '480e04b1', 'd0a397a38bafe195', 'd0a397a38bafe195'), (536860, '480e04c1', 'c8f8da62fbb5a3c5', 'c8f8da62fbb5a3c5'), (538504, '480dfa25480dfa9d', '741e6a27db76e025', '741e6a27db76e025'), (538524, '480dfa99', '882ac94e953cf71b', '882ac94e953cf71b'), (538710, 'f000', '8fd7c47cbe0652ef', '8fd7c47cbe0652ef'), (538770, 'f000', '8fd7c47cbe0652ef', '8fd7c47cbe0652ef'), (539480, '480dfb6d', '6f7f892e2cd79a11', '6f7f892e2cd79a11'), (539808, '480dfa31', '715a51c170aef1af', '715a51c170aef1af'), (542070, 'f000', '8fd7c47cbe0652ef', '8fd7c47cbe0652ef'), (542272, '480dec01', 'afad45c36361f25b', 'afad45c36361f25b'), (542568, '480dec59', '2c1fe047c7867921', '2c1fe047c7867921'), (542612, '480dec5538e00000480dec8139000001480decb1', 'fa3df7f189e6c078', 'fa3df7f189e6c078'), (542640, '480decc1', 'f57dc5ee2980b371', 'f57dc5ee2980b371'), (543068, '480deb7d', 'de912eaf801964cb', 'de912eaf801964cb'), (543084, '480debf1', 'b560cccb263ba03e', 'b560cccb263ba03e'), (543264, '480deae9', '9bb3c732fba4ee75', '9bb3c732fba4ee75'), (543452, '480dea49', '9adf492b81812942', '9adf492b81812942'), (543644, '480de9a5', '9c32bc2cfc145562', '9c32bc2cfc145562'), (547132, '480dd7f4', '3820d906b7c76644', '3820d906b7c76644'), (1454144, '00000000000000000000089000003ac02f4250524530312e73726c00000000002f4250474530312e73726c00000000002f4250454530312e73726c00000000005460803e3880000238a00000280056004082000c3880000048000040280050004082000c3880000148000030280052004082000c38a0000148000020280047004082000c38a0000248000010280045004082000838a000033cdf0001908608f83cc0801690a661003ce0801e38e74dc03907001039270020394700302c0500004182001c54a7203638e761007ce732147ce83b787ce93b787cea3b7890ed8120910d8124912d8128914d812c4e8000203c608016806361002c0300004182000c386000004e800020808d8d904bf227f47c0302143c808016900461043c808016808461002c0400004d820020380000004e8000203ca0801680a561002c05000041820008388000012c0400034e8000203ca0801680a561002c050000380000004c8200208804001d4e8000203cc0801680a661002c050003418200282c05000038a0089038e03ac038000c404182002038a00f2438e03d6838000ee84800001038a00f2c38e03d8838000f0890a6610890e6610c3cc08018b0a6c800b006c80880dc000c7cc62a1490dc00107cc63a1490dc00143cc6000138c683d090dc0018807c000c4e8000203ca0801680a561084e8000203ca0801680a5610c4e8000203d808016818c61002c0c00033c6000a04c8200207c0802a69421ffe09001002493e1001c93c1001893a10014938100103d808016806c66f02c030000408201103fc0802383deb29c3ba000003fe001007c7df85028031000408100407c7dfa145463f87e547c00267f83e378388000207fc5f3784bf5693d2c030000418200147fc4f3784bf569b97f9de3784bffffc47f9fe3784bffffbc3c60801693a366f83fe0801683ff66ec7fe3fb78388010003ca0802380a5b2a04bf568f92c030000408200347fe3fb78388010003ca0802380a5b2984bf568dd2c030000408200183bfff0002c1f00004181ffc0386000003be000003d808016906c66f03d80801693ec66e83fc0802383deb2983fe000207fe3fb78388000207fc5f3784bf568952c030000408200183bfff0002c1f00004181ffe03be000004800000c7fc4f3784bf568fd3c60801693e366fc398000013d608016918b66e08001002483e1001c83c1001883a1001483810010382100207c0803a63c6000b43863f0004e8000203d808016818c61002c0c00033cc000804c8200203cc000b4398000023d608016918b66e04e8000203d808016818c61002c0c00033cc000204c8200203d808016818c66f038c000202c0c00004d8200203d80801680cc66e84e8000203d808016818c61002c0c0003809e01004c820020398000033d608016918b66e03d808016818c66f02c0c00004d8200207d8463784e8000203d808016818c61002c0c00033d2000d04c8200203d2000b44e8000203d808016818c61002c0c0003408200547c0802a69421fff090010014380000013d808016900c66f4380000043d808016900c66e07fc3f3784bf21495380000053d808016900c66e0380000003d808016900c66f480010014382100107c0803a6800100244e8000203d808016818c61002c0c00033fa000804c8200203d808016818c66f42c0c00003ba000004d8200203fa001004e8000203d808016818c61002c0c00033fa000504c8200203ba000004e8000203d808016818c61002c0c00033fa000204c8200203ba000004e8000203d808016818c61002c0c00033fa000104c8200203ba000004e8000203d808016818c61002c0c00033f9f80004c82002057ecaafe7d8c022e280c0b3e40800014558c60267d8c0214398c200048000018398cf4c2558c60263f808016839c66f07d8ce2143d8c80007f8060503d608016818b66e4398c0001918b66e44e8000203d808016808c6108818c610c7c8462143c840001388483d04e8000203d808016808c6108818c610c7c8462143c8400013884a2d04e8000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000003d808016818c6100380008902c0c00004d82002038000f242c0c00034c82002038000f2c4e8000203d808016818c610038003ac02c0c00004d82002038003d682c0c00034c82002038003d884e8000203d808016818c61003c8000013884e6202c0c00004d8200203c8000013884ef5c2c0c00034c8200203c8000013884ef844e8000203cc0801680c661084e8000203d808016818c610c7c1c60504e8000203d808016818c61002c0c00004182003438000f242c0c00034082000838000f2c396300887c005d2c38003d682c0c00034082000838003d883963008c7c005d2c800100144e8000203d808016818c61002c0c00004182003438000f242c0c00034082000838000f2c396300887c005d2c38003d682c0c00034082000838003d883963008c7c005d2c7c671b784e800020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000', 'cbecff30c96ab219', 'cbecff30c96ab219')], 'dol_sha': 'e33e48fd6dda33f490aff3c1aadbe841bb33186f', 'arcs': [('original', [(1899, '78', '27d5482eebd075de'), (1907, '78', '27d5482eebd075de'), (1924, 'ae', '39527c59247a39d1'), (1928, '86', '999a0a8cad102eb5'), (1937, '78', '27d5482eebd075de'), (1948, '8e', '090cbc46c3a13cd0'), (1952, '022003e0', 'db2c7a4a95eb96f6'), (4200, '26e0', 'c1ec1aed342f8316'), (4402, '13e0', 'e8fec6d0144f48d8')], '00ac5de29539943d6ba2998b4095db6217ce9613'), ('Universal-patched', [(1672, 'ae', '39527c59247a39d1'), (1685, '78', '27d5482eebd075de'), (3788, '26e0', 'c1ec1aed342f8316'), (4001, '784538c046c046', '60bd0bae15047d82'), (4011, 'e0', '655f2b71ddfafbcb'), (4024, 'b8b001', '838519d92568637b'), (15028, '56', '6dcd4ce23d88e2ee'), (15036, '50', '6dcd4ce23d88e2ee')], '846ccefa76a9fe51fd35cb53089609e6a7dffb91')]}, 'GPXP01': {'name': 'PAL', 'langs': 'EFIDS', 'shrink_frames': True, 'bneed_off': 1460920, 'dol': [(120408, '48146fd1', 'fabba5cfed994bdb'), (121444, '48146bc5', 'fabba5cfed994bdb'), (122751, '00', '3c363836cf4e1666'), (161476, '4813d4a9', 'a02a42acd7d59781'), (161644, '4813d449', '306e25d73fb33c5e'), (161660, '4813d439', '306e25d73fb33c5e'), (163185, '7f', 'fb3c6e4de85bd9ea'), (163217, '7f', 'fb3c6e4de85bd9ea'), (188416, '4813650d4800003c', 'c9f85163901b5b58'), (188736, '4813698d', 'e473111812cfa85a'), (188748, '481369a9481369cd', '2d25bf6663c0ed31'), (199384, '48133b2d', 'd6e5ab6356b71033'), (241039, '00', 'a42c6cf1de3abfde'), (241067, '00', '3c363836cf4e1666'), (540708, '480e0621', '97c466a85370425c'), (541744, '480e0645', 'd0a397a38bafe195'), (541756, '480e0655', 'c8f8da62fbb5a3c5'), (543400, '480dfbb9480dfc31', '741e6a27db76e025'), (543420, '480dfc2d', '882ac94e953cf71b'), (543606, 'f000', '8fd7c47cbe0652ef'), (543666, 'f000', '8fd7c47cbe0652ef'), (544376, '480dfcd9', '6f7f892e2cd79a11'), (544704, '480dfb9d', '715a51c170aef1af'), (546966, 'f000', '8fd7c47cbe0652ef'), (547168, '480ded95', 'afad45c36361f25b'), (547384, '480deb85', '080112e99d225280'), (547476, '480deb4d', 'f8b9d2157e3a3d1f'), (547512, '480dedbd', '2c1fe047c7867921'), (547556, '480dedb938e00000480dede539000001480dee15', '5c3b273fa67eb076'), (547584, '480dee25', '038c6125a2a1a08b'), (548012, '480dece1', 'de912eaf801964cb'), (548028, '480ded55', 'b560cccb263ba03e'), (548208, '480dec4d', '9bb3c732fba4ee75'), (548396, '480debad', '9adf492b81812942'), (548588, '480deb09', '9c32bc2cfc145562'), (552076, '480dd910', '015f627a8b98a68e'), (1459404, '00000000000000000000089000003ac02f4250524530312e73726c00000000002f4250474530312e73726c00000000002f4250454530312e73726c00000000005460843e38a0000028004250408200505460c63e38a00001280000524182002438a00002280000474182001838a00003280000454182000c38a00000480000203cc0801654a720367ce732145460063e9807759038800002480000243c03bea8388000002800564541820014388000012800504541820008388000023cdf0001908608f83cc0801690a6758c4e8000203c6080168063758c2c0300004182000c386000004e8000209421ffe04bf226d83d808016818c758c2c0c000041820010558c20363d8c8016380c758c280000004e8000203d808016818c758c2c0c000041820010558c20363d8c8016388c758c819b00004e8000207c0302143c808016900475903c8080168084758c2c0400004d820020380000004e8000203ca0801680a5758c2c05000041820008388000012c0400034e8000203ca0801680a5758c2c050000380000004c8200208804001d4e8000203cc0801680a6758c2c050003418200282c05000038a0089038e03ac038000c404182002038a00f2438e03d6838000ee84800001038a00f2c38e03d8838000f0890a6759490e675983cc08018b0a6ddc8b006ddd080dc000c7cc62a1490dc00107cc63a1490dc00143cc6000138c683d090dc0018807c000c4e8000203ca0801680a575944e8000203ca0801680a575984e8000203d808016818c758c2c0c00033c6000a04c8200207c0802a69421ffe09001002493e1001c93c1001893a10014938100103d808016806c7b7c2c030000408201103fc0802383dedb443ba000003fe001007c7df85028031000408100407c7dfa145463f87e547c00267f83e378388000207fc5f3784bf568e52c030000418200147fc4f3784bf569617f9de3784bffffc47f9fe3784bffffbc3c60801693a37b843fe0801683ff7b787fe3fb78388010003ca0802380a5db484bf568a12c030000408200347fe3fb78388010003ca0802380a5db404bf568852c030000408200183bfff0002c1f00004181ffc0386000003be000003d808016906c7b7c3d80801693ec7b743fc0802383dedb403fe000207fe3fb78388000207fc5f3784bf5683d2c030000408200183bfff0002c1f00004181ffe03be000004800000c7fc4f3784bf568a53c60801693e37b88398000013d608016918b7b6c8001002483e1001c83c1001883a1001483810010382100207c0803a63c6000b43863f0004e8000203d808016818c758c2c0c00033cc000804c8200203cc000b4398000023d608016918b7b6c4e8000203d808016818c758c2c0c00033cc000204c8200203d808016818c7b7c38c000202c0c00004d8200203d80801680cc7b744e8000203d808016818c758c2c0c0003809b01004c820020398000033d608016918b7b6c3d808016818c7b7c2c0c00004d8200207d8463784e8000203d808016818c758c2c0c00033d2000d04c8200203d2000b44e8000203d808016818c758c2c0c0003408200547c0802a69421fff090010014380000013d808016900c7b80380000043d808016900c7b6c7f63db784bf21331380000053d808016900c7b6c380000003d808016900c7b8080010014382100107c0803a6396100304e8000203d808016818c758c2c0c00033fa000804c8200203d808016818c7b802c0c00003ba000004d8200203fa001004e8000203d808016818c758c2c0c00033fa000504c8200203ba000004e8000203d808016818c758c2c0c00033fa000204c8200203ba000004e8000203d808016818c758c2c0c00033fa000104c8200203ba000004e8000203d808016818c758c2c0c00033f9f80004c82002057ecaafe7d8c022e280c0b3e40800014558c60267d8c0214398c200048000018398cf4c2558c60263f808016839c7b7c7d8ce2143d8c80007f8060503d608016818b7b70398c0001918b7b704e8000203d808016808c7594818c75987c8462143c840001388483d04e8000203d808016808c7594818c75987c8462143c8400013884a2d04e80002000000000000000000000000000100000000000000000000000000000000000003d808016818c758c380008902c0c00004d82002038000f242c0c00034c82002038000f2c4e8000203d808016818c758c38003ac02c0c00004d82002038003d682c0c00034c82002038003d884e8000203d808016818c758c3c8000013884e6202c0c00004d8200203c8000013884ef5c2c0c00034c8200203c8000013884ef844e8000203cc0801680c675944e8000203d808016818c75987c1c60504e8000203d808016818c758c2c0c00004182003438000f242c0c00034082000838000f2c396300887c005d2c38003d682c0c00034082000838003d883963008c7c005d2c800100144e8000203d808016818c758c2c0c00004182003438000f242c0c00034082000838000f2c396300887c005d2c38003d682c0c00034082000838003d883963008c7c005d2c7c671b784e800020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000', '4d5e37f4417dbc51')], 'dol_sha': '23d743e4f0966e5bffefb975c6741ce7bd5f4925', 'arcs': [('original', [(4552, '26e0', 'c1ec1aed342f8316'), (4762, '0fe0', '5fea284407de70f5')], '8e5cfb811a16b61ae12a6606296e828c6c7d982f')]}}

PAGE, ALIGN_FILE = 0x1000, 0x8000
DISC_SIZE = 1459978240          # a full GameCube disc image (mini-DVD)

def align(x, a): return (x + a - 1) // a * a

# ---------------- ISO reading ----------------
def read_at(f, off, n): f.seek(off); return f.read(n)
def dol_size(h):
    o = struct.unpack(">18I", h[0:72]); s = struct.unpack(">18I", h[144:216])
    return max(a + b for a, b in zip(o, s) if b)
def parse_iso(f):
    boot = bytearray(read_at(f, 0, 0x440)); bi2 = read_at(f, 0x440, 0x2000)
    ah = read_at(f, 0x2440, 0x20)
    app = read_at(f, 0x2440, 0x20 + struct.unpack(">I", ah[0x14:0x18])[0] + struct.unpack(">I", ah[0x18:0x1c])[0])
    dol_off, fst_off, fst_size = struct.unpack(">III", boot[0x420:0x42c])
    dol = read_at(f, dol_off, dol_size(read_at(f, dol_off, 0x100)))
    fst = read_at(f, fst_off, fst_size)
    n = struct.unpack(">I", fst[8:12])[0]; st = fst[n * 12:]
    name = lambda o: st[o:st.index(b"\0", o)].decode("shift_jis", errors="replace")
    files = {}
    def walk(i, end, path):
        while i < end:
            a, b, c = struct.unpack(">III", fst[i*12:i*12+12]); nm = name(a & 0xffffff)
            if a >> 24: walk(i + 1, c, path + nm + "/"); i = c
            else: files[path + nm] = (b, c); i += 1
    walk(1, n, "")
    return boot, bi2, app, dol, files

def h16(b): return hashlib.sha1(b).hexdigest()[:16]

def bad_locations(data, patch):
    return [p[0] for p in patch if h16(data[p[0]:p[0]+len(p[1])//2]) not in p[2:]]

def apply(data, patch):
    data = bytearray(data)
    for p in patch:
        b = bytes.fromhex(p[1]); data[p[0]:p[0]+len(b)] = b
    return bytes(data)

def patch_dol(dol, R):
    bad = bad_locations(dol, R["dol"])
    if bad:
        sys.exit(f"Start.dol: {len(bad)} of {len(R['dol'])} patch locations don't match a supported {R['name']} "
                 f"disc (first at file offset {bad[0]:#x}). Nothing was written.")
    dol = apply(dol, R["dol"])
    return dol, hashlib.sha1(dol).hexdigest() == R["dol_sha"]

def patch_arc(arc, R):
    for name, patch, out_sha in R["arcs"]:
        if not bad_locations(arc, patch):
            arc = apply(arc, patch)
            return arc, name, hashlib.sha1(arc).hexdigest() == out_sha
    sys.exit(f"gbarom.arc doesn't match a supported {R['name']} disc. Nothing was written.")


# ---------------- GBEmulator.arc: smaller GBA frame textures (PAL memory) ----------------
# The 8 GBA border pieces are 16-bit RGB565 (~465 KB). Re-encoding them as CMPR (GameCube DXT1,
# 4-bit) makes them a quarter of the size and frees ~350 KB, which PAL needs for Emerald.
def rgb565_to_rgb(c):
    r = (c >> 11) & 31; g = (c >> 5) & 63; b = c & 31
    return ((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2))

def rgb_to_565(p):
    return ((p[0] >> 3) << 11) | ((p[1] >> 2) << 5) | (p[2] >> 3)

def decode_rgb565(data, w, h):
    px = [[None] * w for _ in range(h)]; i = 0
    for ty in range(0, h, 4):
        for tx in range(0, w, 4):
            for y in range(4):
                for x in range(4):
                    px[ty + y][tx + x] = rgb565_to_rgb(struct.unpack_from('>H', data, i)[0]); i += 2
    return px

def _pal(c0, c1):
    a, b = rgb565_to_rgb(c0), rgb565_to_rgb(c1)
    if c0 > c1:
        return [a, b, tuple((2 * a[k] + b[k]) // 3 for k in range(3)), tuple((a[k] + 2 * b[k]) // 3 for k in range(3))]
    return [a, b, tuple((a[k] + b[k]) // 2 for k in range(3)), (0, 0, 0)]

def _d2(p, q): return (p[0]-q[0])**2 + (p[1]-q[1])**2 + (p[2]-q[2])**2

def encode_block(pix):  # 16 (r,g,b)
    # endpoints along the principal axis (approximated by the farthest pair among a few candidates)
    best = None
    lum = sorted(pix, key=lambda p: p[0] * 299 + p[1] * 587 + p[2] * 114)
    cands = [(lum[0], lum[-1])]
    mn = tuple(min(p[k] for p in pix) for k in range(3)); mx = tuple(max(p[k] for p in pix) for k in range(3))
    cands.append((mn, mx))
    far = max(((p, q) for p in pix for q in pix), key=lambda t: _d2(*t))
    cands.append(far)
    for lo, hi in cands:
        c0, c1 = rgb_to_565(hi), rgb_to_565(lo)
        if c0 < c1: c0, c1 = c1, c0
        if c0 == c1:
            idx = [0] * 16; err = sum(_d2(p, rgb565_to_rgb(c0)) for p in pix)
            pal_c = (c0, c1)
        else:
            pal = _pal(c0, c1)
            idx = []; err = 0
            for p in pix:
                k = min(range(4), key=lambda j: _d2(p, pal[j])); idx.append(k); err += _d2(p, pal[k])
            pal_c = (c0, c1)
        if best is None or err < best[0]: best = (err, pal_c, idx)
    _, (c0, c1), idx = best
    bits = 0
    for k in idx: bits = (bits << 2) | k
    return struct.pack('>HHI', c0, c1, bits)

def encode_cmpr(px, w, h):
    out = bytearray()
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for sy, sx in ((0, 0), (0, 4), (4, 0), (4, 4)):
                blk = [px[ty + sy + y][tx + sx + x] for y in range(4) for x in range(4)]
                out += encode_block(blk)
    return bytes(out)

def bti_rgb565_to_cmpr(bti):
    fmt = bti[0]; w, h = struct.unpack('>HH', bti[2:6]); off = struct.unpack('>I', bti[0x1c:0x20])[0]
    assert fmt == 4 and w % 8 == 0 and h % 8 == 0 and bti[0x18] in (0, 1) and off == 0x20
    px = decode_rgb565(bti[off:off + w * h * 2], w, h)
    hdr = bytearray(bti[:0x20]); hdr[0] = 0x0E
    return bytes(hdr) + encode_cmpr(px, w, h)

def yaz0_dec(d):
    n = struct.unpack(">I", d[4:8])[0]; o = bytearray(); i = 16
    while len(o) < n:
        c = d[i]; i += 1
        for b in range(8):
            if len(o) >= n: break
            if c & (0x80 >> b): o.append(d[i]); i += 1
            else:
                b1, b2 = d[i], d[i+1]; i += 2; dist = ((b1 & 0xf) << 8 | b2) + 1; ln = b1 >> 4
                if ln == 0: ln = d[i] + 0x12; i += 1
                else: ln += 2
                for _ in range(ln): o.append(o[-dist])
    return bytes(o)

def shrink_frames(arc):
    """Return a rebuilt RARC with gba_frame*.bti converted to CMPR, or None if not applicable."""
    if arc[:4] == b"Yaz0": arc = yaz0_dec(arc)
    if arc[:4] != b"RARC": return None
    _, total, hdr, doff, dlen, mram, aram = struct.unpack(">4sIIIIII", arc[:0x1c])
    if mram != dlen or aram != 0: return None
    dbase = doff + 0x20
    nn, noff, ne, eoff, ssz, soff = struct.unpack(">IIIIII", arc[0x20:0x38])
    eoff += 0x20; soff += 0x20
    files = []
    for i in range(ne):
        e = eoff + i * 20
        fid, hsh, typ, _p, nmo, dof, dsz = struct.unpack(">HHBBHII", arc[e:e+16])
        nm = arc[soff+nmo:arc.index(b"\0", soff+nmo)].decode("ascii", "replace")
        if typ & 0x02 or fid == 0xFFFF: continue          # directory entries
        files.append((dof, e, nm, arc[dbase+dof:dbase+dof+dsz]))
    files.sort()
    out = bytearray(arc[:dbase]); newd = bytearray(); changed = 0
    for dof, e, nm, data in files:
        if nm.lower().startswith("gba_frame") and nm.lower().endswith(".bti") and data[0] == 4:
            try: data = bti_rgb565_to_cmpr(data); changed += 1
            except AssertionError: pass
        while len(newd) % 0x20: newd.append(0)
        struct.pack_into(">II", out, e + 8, len(newd), len(data))
        newd += data
    while len(newd) % 0x20: newd.append(0)
    if not changed: return None
    out += newd
    struct.pack_into(">I", out, 4, len(out)); struct.pack_into(">II", out, 0x10, len(newd), len(newd))
    return bytes(out), changed

# ---------------- Emerald packer ----------------
def pack_emerald(rom):
    NP, HDR, OUT = 4096, 0x2000, 0xC40000
    rom = rom.ljust(NP * PAGE, b"\xff")[:NP * PAGE]
    idx, pages, table = {}, [], []
    for p in range(NP):
        pg = rom[p*PAGE:(p+1)*PAGE]
        if pg not in idx: idx[pg] = len(pages); pages.append(pg)
        table.append(idx[pg])
    if len(pages) > (OUT - HDR) // PAGE: sys.exit("Emerald ROM has too many unique pages")
    out = bytearray(OUT); out[:HDR] = struct.pack(">%dH" % NP, *table)
    for i, pg in enumerate(pages): out[HDR+i*PAGE:HDR+(i+1)*PAGE] = pg
    chk = b"".join(out[HDR+t*PAGE:HDR+(t+1)*PAGE] for t in table)
    assert chk == rom, "Emerald pack self-check failed"
    return bytes(out), len(pages)

LANG = {"E": "English", "F": "French", "I": "Italian", "D": "German", "S": "Spanish"}

def check_rom(path, code3, R):
    d = open(path, "rb").read()
    code = d[0xAC:0xB0].decode("ascii", errors="replace")
    ok = [code3 + l for l in R["langs"]]
    if code not in ok:
        sys.exit(f"{path}: game code is {code!r}; the {R['name']} disc needs one of: {', '.join(ok)}")
    if len(d) < 0xF00000: sys.exit(f"{path}: ROM too small ({len(d)} bytes), expected a full 16 MB dump")
    return d, code + "01.srl", LANG[code[3]]

def ask_path(prompt, must_exist=True, optional=False):
    while True:
        v = input(prompt).strip().strip('"').strip("'").strip()
        if not v:
            if optional: return None
            print("  Please enter a path (you can drag the file into this window)."); continue
        if must_exist and not os.path.isfile(v):
            print(f"  File not found: {v}"); continue
        return v

def interactive():
    print("Pokemon Box Ruby & Sapphire (USA/PAL) - FireRed / LeafGreen / Emerald Adventure patcher")
    print("Drag a file into this window and press Enter.\n")
    class A: pass
    a = A()
    a.iso = ask_path("Pokemon Box ISO (USA or PAL): ")
    a.firered   = ask_path("FireRed ROM   (optional, Enter to skip): ", optional=True)
    a.leafgreen = ask_path("LeafGreen ROM (optional, Enter to skip): ", optional=True)
    a.emerald   = ask_path("Emerald ROM   (optional, Enter to skip): ", optional=True)
    base, _ = os.path.splitext(a.iso)
    default = base + " (FRLGE).iso"
    v = input(f"Output ISO [{default}]: ").strip().strip('"').strip("'").strip()
    a.out = v or default
    if os.path.exists(a.out):
        if input(f"{a.out} exists. Overwrite? (y/n): ").strip().lower() != "y": sys.exit("Cancelled.")
    return a

def main():
    if len(sys.argv) > 1:
        ap = argparse.ArgumentParser()
        ap.add_argument("iso"); ap.add_argument("out")
        ap.add_argument("--firered"); ap.add_argument("--leafgreen"); ap.add_argument("--emerald")
        a = ap.parse_args()
    else:
        a = interactive()
    if os.path.abspath(a.iso) == os.path.abspath(a.out): sys.exit("Output must be a different file.")
    src = open(a.iso, "rb")
    boot, bi2, app, dol, files = parse_iso(src)
    gid = boot[:6].decode("ascii", errors="replace")
    if gid not in REGIONS:
        sys.exit(f"Not a supported Pokemon Box disc (game ID {gid}); need GPXE01 (USA) or GPXP01 (PAL).")
    R = REGIONS[gid]
    arcp = next((p for p in files if p.lower() == "gbarom.arc"), None)
    if not arcp: sys.exit("gbarom.arc not found on disc")
    o, s = files[arcp]; arc = read_at(src, o, s)
    dol, dol_exact = patch_dol(dol, R)
    arc, kind, arc_exact = patch_arc(arc, R)
    print(f"Detected: {R['name']} ({gid}), {kind} disc")
    if not dol_exact or not arc_exact:
        print("Note: your Start.dol/gbarom.arc differ from the author's elsewhere (other mods?); patched anyway.")
    print("Patched Start.dol and gbarom.arc")
    shrunk = None
    if R.get("shrink_frames"):
        gbe = next((p for p in files if p.lower().split("/")[-1] == "gbemulator.arc"), None)
        if gbe:
            print("Compressing GBA frame textures in GBEmulator.arc (frees memory for Emerald)...")
            o2, s2 = files[gbe]; res = shrink_frames(read_at(src, o2, s2))
            if res: shrunk = (gbe, res[0]); print(f"  {res[1]} textures converted, {s2 // 1024} KB -> {len(res[0]) // 1024} KB")
            else: print("  Note: GBEmulator.arc not in the expected format; left unchanged.")

    merged = {p: ("iso", o, s) for p, (o, s) in files.items()}
    merged[arcp] = ("mem", arc, len(arc))
    if shrunk: merged[shrunk[0]] = ("mem", shrunk[1], len(shrunk[1]))
    if a.firered:
        d, fn, lang = check_rom(a.firered, "BPR", R); merged[fn] = ("mem", d, len(d)); print(f"Added FireRed ({lang}) as {fn}")
    if a.leafgreen:
        d, fn, lang = check_rom(a.leafgreen, "BPG", R); merged[fn] = ("mem", d, len(d)); print(f"Added LeafGreen ({lang}) as {fn}")
    if a.emerald:
        d, fn, lang = check_rom(a.emerald, "BPE", R); p, n = pack_emerald(d)
        merged[fn] = ("mem", p, len(p)); print(f"Added Emerald ({lang}) as {fn} (packed, {n} unique pages)")
        extra = max(1, n - (0xB40000 - 0x2000) // PAGE) * PAGE
        # tell Start.dol how much extra memory this Emerald needs, so it takes no more than that
        o = R["bneed_off"]; dol = dol[:o] + struct.pack(">I", extra) + dol[o+4:]
        if extra > 0xF0000:
            print(f"Warning: this Emerald needs {extra // 1024} KB of extra memory; PAL Box has about 990 KB free, "
                  "so it may not run on PAL.")

    tree = {}
    for p in merged:
        node = tree; parts = p.split("/")
        for x in parts[:-1]: node = node.setdefault(x, {})
        node[parts[-1]] = p
    ents = [{"dir": True, "name": "", "parent": 0}]
    def add(node, parent):
        for nm in sorted(node, key=str.lower):
            v = node[nm]
            if isinstance(v, dict):
                i = len(ents); e = {"dir": True, "name": nm, "parent": parent}; ents.append(e); add(v, i); e["next"] = len(ents)
            else: ents.append({"dir": False, "name": nm, "key": v, "size": merged[v][2]})
    add(tree, 0); ents[0]["next"] = len(ents)
    strtab = bytearray(); ents[0]["noff"] = 0
    for e in ents[1:]: e["noff"] = len(strtab); strtab += e["name"].encode("shift_jis", errors="replace") + b"\0"
    fst_size = len(ents) * 12 + len(strtab)
    dol_off = align(0x2440 + len(app), 0x100); fst_off = align(dol_off + len(dol), 0x100)
    pos = align(fst_off + fst_size, ALIGN_FILE)
    for e in ents[1:]:
        if not e["dir"]: e["off"] = pos; pos = align(pos + e["size"], ALIGN_FILE if e["size"] else 4)
    fst = bytearray()
    for e in ents:
        fst += struct.pack(">III", (1 << 24) | e["noff"], e["parent"], e["next"]) if e["dir"] else struct.pack(">III", e["noff"], e["off"], e["size"])
    fst += strtab
    struct.pack_into(">IIII", boot, 0x420, dol_off, fst_off, fst_size, fst_size)
    with open(a.out, "wb") as f:
        f.write(boot); f.write(bi2); f.seek(0x2440); f.write(app)
        f.seek(dol_off); f.write(dol); f.seek(fst_off); f.write(fst)
        for e in ents[1:]:
            if e["dir"]: continue
            f.seek(e["off"]); kind, x, size = merged[e["key"]]
            if kind == "iso":
                src.seek(x); left = size
                while left: c = src.read(min(left, 1 << 22)); f.write(c); left -= len(c)
            else: f.write(x)
        # full-size image: pad to a whole GameCube disc (or the original ISO's size if larger)
        size = max(pos, DISC_SIZE, os.path.getsize(a.iso))
        f.truncate(size)
    if pos > DISC_SIZE:
        print(f"Note: the files need {pos/1048576:.1f} MiB, more than a real GameCube disc holds "
              f"({DISC_SIZE/1048576:.1f} MiB). It works in Dolphin, but won't fit a disc.")
    print(f"Done: {a.out} ({size/1048576:.1f} MiB image, {pos/1048576:.1f} MiB used)")

if __name__ == "__main__":
    interactive_mode = len(sys.argv) == 1
    try:
        main()
    except SystemExit as e:
        if e.code not in (None, 0): print(f"\nERROR: {e.code}" if isinstance(e.code, str) else "\nStopped.")
    except Exception as e:
        print(f"\nERROR: {e}")
    if interactive_mode:
        input("\nPress Enter to close...")