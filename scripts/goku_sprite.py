"""Pixel-art Goku and Kamehameha for the activity panel, built with the standard library.

Goku is the 30×46 CSS box-shadow sprite the profile owner picked, transcribed
pixel for pixel. It has a single standing pose, so the charge, fire and run
frames are small pixel edits of it. All frames face right. Every frame is a
list of strings, one character per pixel, with "." for transparent.
"""
import math

PALETTE = {
    "k": "#000000", "W": "#ffffff", "g": "#666666", "P": "#f4e6e3",
    "O": "#ef6004", "B": "#044eb1", "R": "#fe0003", "Y": "#ffcc27",
    # Kamehameha
    "1": "#1b4fd1", "2": "#2f8cf0", "3": "#5cc8fa", "4": "#b8ecff", "5": "#ffffff",
}

W, H = 33, 46
HANDS = (32.5, 25.5)      # fire frame: front edge and centre of the stacked palms
CHARGE_HANDS = (8, 33)    # charge frame: the hands cupped at the back hip

SPRITE = [
    ".................kkkkk........",
    "...............kkkkk..........",
    "..............kkkkk...........",
    ".............kkkkkk...........",
    ".............kkkkk..kkkk......",
    "............kkkkkk.kkkkkkk....",
    "............kkkkkkkkkkkkkkk...",
    "............kkkkkkkkkkkkkkkk..",
    "............kkkkkkkkkkkkkkkkk.",
    "..........kkkkkkkkkkkkkkkkkkkk",
    ".........kkkkkkkkkkkkkkkkk....",
    "........kkkkkkkkkkkkkkkk......",
    "........kkkkkkkkkkkkkkk.......",
    "....kkkkkkkkkkkkkkkkkkkkk.....",
    "......kkkkkkkkkkkPkkkkkkkkk...",
    "...kkkkkkkkkkPkkkPPPkkkkkkkk..",
    "kkkkkkkkkkkkkkkkkPPPPkkkkk....",
    "..kkkkkkkkPkkPPkkPPPPPkkk.....",
    "....kkkkkkPPkPk..kPPPk.k......",
    "...kkkkkkkPPPPk..kkPkk........",
    "........kkkkPPPPPPPPPk........",
    ".......kkkkOkPPPPPPPk.........",
    ".........kOOOkkPPPPkOk........",
    "........kBkOOkBkkkkBkOk.......",
    ".......kBBBkOkBBBBBBkOk.......",
    ".......kBBBkOOkBBBBBkOk.......",
    ".......kkBBkOOOkkkkkOOk.......",
    "......kPPkk.kOOOOOOOOkk.......",
    "......kPPPk.kkkkkkkkkkk.......",
    "......kPPk..kBBBBBBBBkPk......",
    "......kBBk.kkkkkkkkkkkPk......",
    ".....kBBBBkOOOOOOkOOOkBBk.....",
    ".....kPPPPkOOOOOOkOOOkBPk.....",
    ".....kPPkPkOOOOOOkOOOOkPk.....",
    ".....kPPkkkOOOOOOkOOOOkPk.....",
    "......kkPkOOOOOOOkOOOOkk......",
    "........kkOOOOOOOkOOOOOk......",
    "........kOOOOOOOkkOOOOOk......",
    "........kOOOOOOk.kOOOOOk......",
    "........kOOOOOk..kkkkkk.......",
    ".......kkkkkkk...kBBBRk.......",
    ".......kBRBBk....kBBBRk.......",
    "......kYYRBBk....kBBYYRk......",
    "......kBRYYk......kYBBBRk.....",
    "......kBRBBk.......kkkkkk.....",
    "......kkkkkk..................",
]


def _grid():
    return [list(r.ljust(W, ".")) for r in SPRITE]


def _erase(g, row, c0, c1):
    for x in range(c0, c1 + 1):
        g[row][x] = "."


def _paint(g, row, col, s):
    """Overlay s at (col, row); "." leaves the pixel underneath alone."""
    for i, c in enumerate(s):
        if c != ".":
            g[row][col + i] = c


def _drop_near_arm(g):
    """Remove the arm hanging on the right of the sprite."""
    for row, c0, c1 in ((29, 22, 23), (30, 22, 23), (31, 22, 24), (32, 22, 24), (33, 23, 24), (34, 23, 24), (35, 23, 23)):
        _erase(g, row, c0, c1)


def _fire():
    g = _grid()
    _drop_near_arm(g)
    # the far arm goes behind the body: clear it and close the shoulder
    for row, c0, c1 in ((27, 6, 10), (28, 6, 10), (29, 6, 9), (30, 6, 9), (31, 5, 9), (32, 5, 9), (33, 5, 9), (34, 5, 9), (35, 6, 8)):
        _erase(g, row, c0, c1)
    _paint(g, 27, 9, "kkk")
    _paint(g, 35, 9, "k")
    # the near arm thrust out, palms stacked
    for row, s in ((21, "......kkk.."), (22, ".....kPPPk."), (23, ".kkkkkPPPPk"), (24, ".BBPPBPPPPk"), (25, ".BBPPBkkkPk"),
                   (26, ".BBPPBPPPPk"), (27, ".kkkkkPPPPk"), (28, ".....kPPPk."), (29, "......kkk..")):
        _paint(g, row, 22, s)
    return g


def _charge():
    g = _grid()
    _drop_near_arm(g)
    # the near arm keeps its upper half and swings its forearm across the waist to the far fist
    _paint(g, 29, 22, "Pk")
    _paint(g, 30, 10, "k")
    _paint(g, 30, 22, "Pk")
    _paint(g, 31, 5, "kPPPPBBPPPPPPPPPPPk")
    _paint(g, 32, 5, "kPPPPBBPPPPPPPPPPPk")
    _paint(g, 33, 5, "kPPkPkkkkkkkkkkkkkk")
    return g


def _run(step):
    """Two running frames: the feet trade places, one lifted, one planted."""
    g = _grid()
    if step:
        left = [row[6:13] for row in g[40:46]]
        for r in range(40, 46):
            _erase(g, r, 6, 12)
        for i, row in enumerate(left):
            _paint(g, 38 + i, 6, "".join(row))
        right = [row[17:26] for row in g[40:45]]
        for r in range(40, 45):
            _erase(g, r, 17, 25)
        _paint(g, 40, 17, "kOOOOk")
        for i, row in enumerate(right):
            _paint(g, 41 + i, 17, "".join(row))
    return g


def frames():
    out = {"win": _grid(), "fire": _fire(), "charge": _charge(), "run1": _run(0), "run2": _run(1)}
    return {k: ["".join(r) for r in g] for k, g in out.items()}


# ───────────────────────────── Kamehameha ─────────────────────────────
def beam(length, half=6, seed=7):
    """A horizontal pixel beam `length` px long: dark-blue rim, cyan bands, white core, flowing edges."""
    rows = [["."] * length for _ in range(2 * half + 1)]
    for x in range(length):
        top = half - 1 + round(.9 * math.sin(x * .3 + seed))
        bot = half - 1 + round(.9 * math.sin(x * .24 + seed + 2))
        glow = .2 + .1 * (math.sin(x * .45 + seed) > .6)   # the white core swells now and then
        for y in range(-top, bot + 1):
            edge = top if y < 0 else bot
            a = abs(y) / max(edge, 1)
            rows[y + half][x] = "1" if abs(y) == edge else "2" if a > .74 else "3" if a > .5 else "4" if a > glow + .1 else "5"
    return ["".join(r) for r in rows]


def blob(r, spikes=0, seed=0):
    """A round ki blob of radius r with optional flame spikes."""
    size = 2 * (r + 3) + 1
    c = r + 3
    rows = [["."] * size for _ in range(size)]
    for y in range(size):
        for x in range(size):
            dx, dy = x - c, y - c
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            edge = r + (2.2 * max(0, math.cos(spikes * ang + seed)) ** 6 if spikes else 0)
            if d <= edge:
                f = d / edge
                rows[y][x] = "5" if f < .45 else "4" if f < .65 else "3" if f < .8 else "2" if f < .92 else "1"
    return ["".join(r) for r in rows]


def burst(r, ring=False):
    """Explosion frame: a filled flash, or a broken ring of sparks."""
    size = 2 * r + 3
    c = r + 1
    rows = [["."] * size for _ in range(size)]
    for y in range(size):
        for x in range(size):
            dx, dy = x - c, y - c
            d = math.hypot(dx, dy)
            if ring:
                ang = math.degrees(math.atan2(dy, dx)) % 45
                if r - 2 <= d <= r and ang < 26:
                    rows[y][x] = "3" if d > r - 1 else "4"
            elif d <= r:
                f = d / r
                rows[y][x] = "5" if f < .5 else "4" if f < .75 else "3" if f < .9 else "2"
    return ["".join(r) for r in rows]


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
