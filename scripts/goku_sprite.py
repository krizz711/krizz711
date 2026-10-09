"""Pixel-art Goku and Kamehameha for the activity panel, built with the standard library.

Goku is drawn procedurally: each pose is a skeleton whose limbs are rasterised as
tapered capsules with three-tone shading (light from the top right). A
hand-pixelled head goes on top, and every part gets a dark outline the way
hand-made sprites do. All frames face right. Every frame is a list of strings,
one character per pixel, with "." for transparent.
"""
import math

PALETTE = {
    "k": "#08070c",                                   # outline
    "K": "#1c1b24", "h": "#0f0e15", "H": "#55546e",   # hair: base, shade, highlight
    "S": "#ffdcb5", "T": "#f5b384", "s": "#d48250",   # skin: light, base, shade
    "Y": "#ffc93c", "O": "#ff8a12", "o": "#de560c", "r": "#9a3206",   # gi
    "L": "#79b2ff", "B": "#2f6fe0", "b": "#1a3c8f",   # blue
    "W": "#ffffff", "E": "#120f1c", "M": "#8c2f14",
    # Kamehameha
    "1": "#1b4fd1", "2": "#2f8cf0", "3": "#5cc8fa", "4": "#b8ecff", "5": "#ffffff",
}
RAMPS = {"gi": "YOor", "skin": "STss", "blue": "LBbb"}
LIGHT = (.6, -.8)

W, H = 40, 53

# Hand-pixelled head, facing right. K hair, S/T/s skin, E brows and pupils, W eye whites, M mouth.
HEAD = [
    "................K.........",
    "...............KK.........",
    "........K.....KKK....K....",
    "........KK...KKKK...KK....",
    ".........KK.KKKKK..KKK....",
    ".........KKKKKKKK.KKKK....",
    "..KK......KKKKKKKKKKK.....",
    "...KKKK..KKKKKKKKKKKKK..K.",
    ".....KKKKKKKKKKKKKKKKKKKK.",
    "KKK...KKKKKKKKKKKKKKKKKKK.",
    "..KKKKKKKKKKKKKKKKKKKKKKKK",
    "....KKKKKKKKKKKKKKKKKKKKKK",
    "KKKKKKKKKKKKKKKKKKKKKKKKKK",
    ".KKKKKKKKKKKKKKTKKKKTKKKKK",
    "...KKKKKKKKKKKTTKKKTTTKKTK",
    "....KKKKKKKKKTTTEEKTTTTEEK",
    "......KKKKKKsTTTWETTTTTWET",
    ".......KKKKKsTTTWETTTTTWET",
    "........KKKsTTTTTTTTTTTTTT",
    ".........KKsTTTTTTTTTTsTTT",
    "..........KsTTTTTTTTTTTT..",
    "...........ssTTTTTMMTTT...",
    ".............sssTTTTTT....",
    "...............ssss.......",
]
YELL = ["...........ssTTTTMMMTTT...", ".............sssTMMMTT...."]

# Skeletons, in sprite pixels. Limbs are (from, to, radius_from, radius_to, material).
POSES = {
    "fire": {
        "head": (11, 1), "yell": True,
        "back": [((16, 33), (11, 38), 3.8, 3.2, "gi"), ((11, 38), (7, 42.5), 3.2, 2.6, "gi"),
                 ((7, 43), (3.5, 44.5), 2, 1.8, "blue"),
                 ((24, 24), (29, 25), 2.9, 2.2, "gi"), ((29, 25), (32.5, 25), 1.8, 1.7, "skin"),
                 ((32.2, 25), (33.6, 25), 2.1, 2.1, "blue"), ((35.2, 24.8), (35.4, 24.8), 2.2, 2.2, "skin")],
        "torso": ((21.5, 25), (19, 32), 5.8, 4.8),
        "belt": ((13.5, 33), (23.5, 33)),
        "front": [((21, 34), (27, 38), 3.8, 3.2, "gi"), ((27, 38), (29, 42.5), 3.2, 2.6, "gi"),
                  ((29, 43), (33, 44.5), 2, 1.8, "blue")],
        "arm": [((23, 26), (28, 27.5), 2.9, 2.2, "gi"), ((28, 27.5), (32.5, 27.5), 1.8, 1.7, "skin"),
                ((32.2, 27.5), (33.6, 27.5), 2.1, 2.1, "blue"), ((35.2, 27.6), (35.4, 27.6), 2.2, 2.2, "skin")],
    },
    "charge": {
        "head": (10, 1), "yell": False,
        "back": [((16, 33), (10, 37), 3.8, 3.2, "gi"), ((10, 37), (6, 42.5), 3.2, 2.6, "gi"),
                 ((6, 43), (2.5, 44.5), 2, 1.8, "blue"),
                 ((22, 24), (16, 27), 2.9, 2.2, "gi"), ((16, 27), (11, 29), 1.8, 1.7, "skin"),
                 ((11.5, 29), (10, 29.5), 2.1, 2.1, "blue"), ((8, 29.5), (7.8, 29.5), 2.3, 2.3, "skin")],
        "torso": ((19.5, 25), (18.5, 32), 5.8, 4.8),
        "belt": ((13, 33), (23, 33)),
        "front": [((21, 34), (27, 37), 3.8, 3.2, "gi"), ((27, 37), (30, 42.5), 3.2, 2.6, "gi"),
                  ((30, 43), (34, 44.5), 2, 1.8, "blue")],
        "arm": [((20, 26), (15, 29.5), 2.9, 2.2, "gi"), ((15, 29.5), (11, 31.5), 1.8, 1.7, "skin"),
                ((11.5, 31.5), (10, 32), 2.1, 2.1, "blue"), ((8, 32), (7.8, 32), 2.3, 2.3, "skin")],
    },
    "run1": {
        "head": (12, 1), "yell": False,
        "back": [((16, 33), (10, 37), 3.8, 3.2, "gi"), ((10, 37), (4, 38.5), 3.2, 2.6, "gi"),
                 ((3.5, 39), (1.5, 41.5), 2, 1.8, "blue"),
                 ((24, 24), (28, 28), 2.9, 2.2, "gi"), ((28, 28), (31.5, 25), 1.8, 1.7, "skin"),
                 ((31.2, 25.3), (32.4, 24.2), 2.1, 2.1, "blue"), ((33.6, 23), (33.8, 23), 2.2, 2.2, "skin")],
        "torso": ((22, 25), (19, 32), 5.8, 4.8),
        "belt": ((14, 33), (24, 33)),
        "front": [((21, 34), (28, 36), 3.8, 3.2, "gi"), ((28, 36), (30, 42), 3.2, 2.6, "gi"),
                  ((30, 42.8), (34, 44.3), 2, 1.8, "blue")],
        "arm": [((21, 26), (16, 29.5), 2.9, 2.2, "gi"), ((16, 29.5), (13, 26.5), 1.8, 1.7, "skin"),
                ((13.3, 26.8), (12.3, 25.8), 2.1, 2.1, "blue"), ((11, 24.5), (10.8, 24.3), 2.2, 2.2, "skin")],
    },
    "run2": {
        "head": (12, 0), "yell": False,
        "back": [((17, 32), (19, 37), 3.8, 3.2, "gi"), ((19, 37), (13, 39.5), 3.2, 2.6, "gi"),
                 ((12.5, 40), (10, 41.5), 2, 1.8, "blue"),
                 ((24, 23.5), (27, 28), 2.9, 2.2, "gi"), ((27, 28), (29.5, 26), 1.8, 1.7, "skin"),
                 ((29.3, 26.2), (30.3, 25.3), 2.1, 2.1, "blue"), ((31.5, 24.3), (31.7, 24.1), 2.2, 2.2, "skin")],
        "torso": ((21.5, 24), (19, 31), 5.8, 4.8),
        "belt": ((14, 32), (24, 32)),
        "front": [((21, 33), (24, 38), 3.8, 3.2, "gi"), ((24, 38), (23, 42.5), 3.2, 2.6, "gi"),
                  ((23, 43), (27, 44.5), 2, 1.8, "blue")],
        "arm": [((21, 25), (17, 29), 2.9, 2.2, "gi"), ((17, 29), (15, 26), 1.8, 1.7, "skin"),
                ((15.2, 26.3), (14.5, 25.3), 2.1, 2.1, "blue"), ((13.5, 24.2), (13.3, 24), 2.2, 2.2, "skin")],
    },
    "win": {
        "head": (11, 1), "yell": False,
        "back": [((16, 33), (12, 38), 3.8, 3.2, "gi"), ((12, 38), (10, 42.5), 3.2, 2.6, "gi"),
                 ((10, 43), (6.5, 44.5), 2, 1.8, "blue"),
                 ((17, 24), (13, 28), 2.9, 2.2, "gi"), ((13, 28), (16, 31), 1.8, 1.7, "skin"),
                 ((16, 31), (17, 31.5), 2.1, 2.1, "blue"), ((18.5, 31.5), (18.7, 31.5), 2.2, 2.2, "skin")],
        "torso": ((20.5, 25), (19, 32), 5.8, 4.8),
        "belt": ((13.5, 33), (23.5, 33)),
        "front": [((21, 34), (25, 38), 3.8, 3.2, "gi"), ((25, 38), (27, 42.5), 3.2, 2.6, "gi"),
                  ((27, 43), (31, 44.5), 2, 1.8, "blue")],
        "arm": [((24, 23.5), (30, 21), 2.9, 2.2, "gi"), ((30, 21), (32, 14), 1.8, 1.7, "skin"),
                ((32, 14.5), (32.3, 13), 2.1, 2.1, "blue"), ((32.6, 10.8), (32.6, 10.6), 2.4, 2.4, "skin")],
    },
}
POSES["idle"] = POSES["run2"]



def _y(y):
    """Poses are authored on a short body; stretch it so the head sits on a proper torso and legs."""
    return 28 + (y - 24) * 11 / 9 if y <= 33 else 39 + (y - 33) * 1.09


HANDS = (37, _y(26.2))        # fire frame: front edge and centre of the stacked palms
CHARGE_HANDS = (8, _y(30.7))  # charge frame: the cupped hands at the back hip


def _capsule(a, b, ra, rb, ramp):
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    ll = dx * dx + dy * dy or 1e-9
    r = max(ra, rb)
    out = {}
    for y in range(int(min(ay, by) - r) - 1, int(max(ay, by) + r) + 2):
        for x in range(int(min(ax, bx) - r) - 1, int(max(ax, bx) + r) + 2):
            px, py = x + .5, y + .5
            t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / ll))
            cx, cy = ax + t * dx, ay + t * dy
            rad = ra + (rb - ra) * t
            d = math.hypot(px - cx, py - cy)
            if d <= rad:
                v = ((px - cx) * LIGHT[0] + (py - cy) * LIGHT[1]) / max(d, 1e-9) if d > .35 else 0
                e = d / rad
                out[(x, y)] = ramp[0] if v > .45 and e > .3 else ramp[3] if v < -.55 and e > .75 else ramp[2] if v < -.2 else ramp[1]
    return out


class _Canvas:
    def __init__(self):
        self.px = {}

    def part(self, pixels, outline=True):
        if outline:
            ring = {(x + i, y + j) for x, y in pixels for i in (-1, 0, 1) for j in (-1, 0, 1)} - pixels.keys()
            for p in ring:
                self.px[p] = "k"
        self.px.update(pixels)


def _head(ox, oy, yell):
    rows = HEAD[:21] + (YELL if yell else HEAD[21:23]) + HEAD[23:]
    px = {}
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c != ".":
                px[(ox + x, oy + y)] = c
    # rim-light the hair: highlight edges facing the light, shade the ones away from it
    for (x, y), c in list(px.items()):
        if c == "K":
            if (x + 1, y - 1) not in px or (x, y - 1) not in px:
                px[(x, y)] = "H"
            elif (x - 1, y + 1) not in px:
                px[(x, y)] = "h"
    return px


def _pose(p):
    def lift(limb):
        (ax, ay), (bx, by) = limb[0], limb[1]
        return ((ax, _y(ay)), (bx, _y(by))) + tuple(limb[2:])
    p = dict(p, back=[lift(l) for l in p["back"]], front=[lift(l) for l in p["front"]], arm=[lift(l) for l in p["arm"]],
             torso=lift(p["torso"]), belt=lift(p["belt"]))
    cv = _Canvas()
    for limb in p["back"]:
        cv.part(_capsule(*limb[:4], RAMPS[limb[4]]))
    torso = _capsule(p["torso"][0], p["torso"][1], p["torso"][2], p["torso"][3], RAMPS["gi"])
    cv.part(torso)
    # blue undershirt showing in the gi's V-neck
    (tx, ty) = p["torso"][0]
    cv.part({(int(tx) + i, int(ty) - 2 + j): "L" if j == 0 else "B" for j in range(3) for i in range(j - 1, 4 - j)}, outline=False)
    a, b = p["belt"]
    cv.part(_capsule(a, b, 1.6, 1.6, RAMPS["blue"]))
    cv.part(_capsule((a[0] + .5, a[1] + 1), (a[0] - 1.5, a[1] + 3), 1.1, .9, RAMPS["blue"]))  # belt tail
    for limb in p["front"]:
        cv.part(_capsule(*limb[:4], RAMPS[limb[4]]))
    cv.part(_head(*p["head"], p["yell"]))
    for limb in p["arm"]:
        cv.part(_capsule(*limb[:4], RAMPS[limb[4]]))
    rows = [["."] * W for _ in range(H)]
    for (x, y), c in cv.px.items():
        if 0 <= x < W and 0 <= y < H:
            rows[y][x] = c
    return ["".join(r) for r in rows]


def frames():
    return {name: _pose(p) for name, p in POSES.items()}


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
