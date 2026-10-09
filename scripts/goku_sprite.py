"""Pixel-art micro kid Goku for the activity panel: 22×27 px frames, facing right.

Each frame is a list of rows; one character per pixel, "." is transparent.
"""

PALETTE = {"K": "#17151f", "H": "#3b3f56", "S": "#ffd3ad", "s": "#e8a57a", "E": "#17151f", "M": "#b4532a",
           "O": "#ff7a1a", "o": "#c9500f", "B": "#2f6fe0", "b": "#1b3f91"}

HEAD = [
    "........K....K........",
    ".......KK...KK...K....",
    "....K..KKK.KKK..KK....",
    ".....KKKHKKKHKKKK.....",
    "...KKKKKKKKKKKKKKKK...",
    "..KKKKKHKKKKHKKKKKKK..",
    "KKKHKKKKKKKKKKKKKKKK..",
    ".KKKKKKKKKKKKKSKKKSK..",
    "KKKKKKKKKKKKSSSSKSSSK.",
    "..KKKKKKKKSSKKSSSKKS..",
    "...KKKKKKSSSSESSSSES..",
    ".KKKKKKKSsSSSESSSSES..",
    "...KKKKKSsSSSESSSSES..",
    "....KKKKSSSSSSSSMMSs..",
    "......KKsSSSSSSSSSs...",
    ".........sssSSSSs.....",
]

BODY = {
    "run1": [
        ".........oOBBOOo......",
        "........oOOOBOOOOBS...",
        ".....SBOOOOOOOOo......",
        "........oOOOOOOo......",
        "........bBBBBBBBb.....",
        ".......oOOOOOOOOOo....",
        "......oOOOo..oOOOOO...",
        ".....oOOOo.....oOOOO..",
        "...oOOOo........oOOOb.",
        "..bBBb...........bBBB.",
        ".bBBB..............BB.",
    ],
    "run2": [
        ".........oOBBOOo......",
        "........oOOOBOOOo.....",
        "........oOBSOOOOo.....",
        "........oOOOOOOOo.....",
        "........bBBBBBBBb.....",
        ".......oOOOOOOOOo.....",
        "........oOOOOOOOo.....",
        ".........oOOooOOO.....",
        ".........oOO..oOOb....",
        "........bBBb...bBBB...",
        "........bBBBB.........",
    ],
    "charge": [
        ".........oOBBOOo......",
        "........oOOOBOOOo.....",
        "......OOoOOOOOOOo.....",
        "....BOOooOOOOOOOo.....",
        "...SSBbBBBBBBBBBb.....",
        "...SS..oOOOOOOOOOo....",
        "......oOOOo...oOOOOo..",
        ".....oOOOo......oOOOo.",
        "....oOOOo........oOOO.",
        "....bBBb.........bBBb.",
        "...bBBBB.........bBBBB",
    ],
    "fire": [
        ".........oOBBOOo......",
        "........oOOOBOOOOOOBSS",
        "........oOOOOOOOOOOBSS",
        "........oOOOOOOo......",
        "........bBBBBBBBb.....",
        ".......oOOOOOOOOOo....",
        "......oOOOo..oOOOOo...",
        ".....oOOOo....oOOOo...",
        "....oOOOo......oOOOo..",
        "....bBBb........bBBb..",
        "...bBBBB........bBBBB.",
    ],
    "win": [
        ".........oOBBOOOOOOO..",
        "........oOOOBOOOo.....",
        "........oOOOOOOOOo....",
        "......SBoOOOOOOOo.....",
        "......SSbBBBBBBBb.....",
        ".......oOOOOOOOOOo....",
        ".......oOOOo.oOOOo....",
        ".......oOOo...oOOo....",
        ".......oOOo...oOOo....",
        "......bBBBb...bBBBb...",
        "......bBBBB...bBBBB...",
    ],
}

# Frame-specific touches on the shared head: an open, yelling mouth when firing,
# and the raised arm and fist of the victory pose.
PATCHES = {
    "fire": [(16, 13, "MM"), (16, 14, "MM")],
    "win": [(19, 6, "SS"), (19, 7, "SS"), (19, 8, "BB")] + [(19, y, "OO") for y in range(9, 16)],
}

W, H = 22, 27
HANDS = (22, 18)         # fire frame: front edge and centre row of the hands
CHARGE_HANDS = (4, 21)   # charge frame: the cupped hands at the back hip


def frames():
    out = {}
    for name, body in BODY.items():
        rows = HEAD + body
        for x, y, s in PATCHES.get(name, ()):
            rows[y] = rows[y][:x] + s + rows[y][x + len(s):]
        assert len(rows) == H and all(len(r) == W for r in rows), name
        out[name] = rows
    return out


def to_svg(rows, px, ox, oy):
    """Rects for one frame, horizontal runs merged and grouped by colour."""
    by_colour = {}
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            c = row[x]
            n = 1
            while x + n < len(row) and row[x + n] == c:
                n += 1
            if c != ".":
                by_colour.setdefault(PALETTE[c], []).append(
                    f'<rect x="{ox + x * px:.2f}" y="{oy + y * px:.2f}" width="{n * px + .05:.2f}" height="{px + .05:.2f}"/>')
            x += n
    return "".join(f'<g fill="{c}">{"".join(r)}</g>' for c, r in by_colour.items())
