"""Builds the "Training Ground" panel of the profile README.

A pixel-art Goku runs around a contribution-style grid, charging up in a cyan
aura and firing a Kamehameha at random spots. Each blast lights a small damage
area (one to four cells) in GitHub greens. The grid is decorative: the sites are
re-rolled on every build, so it never shows the real commit history; only the
yearly contribution total in the corner is live data. It is all SMIL, so it
plays inside a README <img>, then resets and loops.

Runs in GitHub Actions (.github/workflows/profile-assets.yml) with the
workflow's GITHUB_TOKEN and nothing but the standard library.

    python scripts/build_activity.py <login> dist/activity.svg
    python scripts/build_activity.py --mock dist/activity.svg      # offline preview
"""
import json
import math
import os
import random
import sys
import urllib.request
from datetime import datetime, timezone
from xml.etree import ElementTree

import goku_sprite as gs

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection { contributionCalendar { totalContributions } }
  }
}
"""

INTER = "'Inter','Segoe UI',Helvetica,Arial,sans-serif"
INK, INK2, MUTED, LINE = "#0f172a", "#1f2937", "#6b7280", "#e5e7eb"
GREENS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
FLASH = "#e0fbff"
HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 1024, 252
STEP, CS = 17, 13                 # grid pitch and cell size
X0, Y0 = 64, 98                   # top-left cell
WEEKS, BLASTS = 53, 34
PX = 1.25                         # one sprite pixel
HAND_X = (gs.HANDS[0] - gs.W / 2) * PX
REACH = 3 * STEP                  # how far from its target Goku fires
BEAM_LEN = math.ceil(REACH / PX) + 2   # the pixel beam, in sprite pixels
SPEED = 520                       # running speed, px/s
CHARGE, EXTEND, HOLD, FADE = .24, .12, .14, .1
INTRO, VICTORY, RESET = .5, 2.2, .7


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-activity"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def mock():
    return {"totalContributions": 523}


# ───────────────────────────── animation helpers ─────────────────────────────
def animate(attr, pts, T, discrete=False, transform=None):
    """One looping SMIL animation from (seconds, value) keyframes on a T-second cycle."""
    if discrete:
        pts = [p for i, p in enumerate(pts) if i == 0 or p[1] != pts[i - 1][1]]
    if pts[0][0] > 0:
        pts = [(0, pts[0][1])] + pts
    if not discrete and pts[-1][0] < T:
        pts = pts + [(T, pts[-1][1])]
    keys, last = [], -1.0
    for t, _ in pts:
        k = max(round(t / T, 5), round(last + 1e-5, 5))
        keys.append(k)
        last = k
    if not discrete:
        keys[-1] = 1
    tag = "animateTransform" if transform else "animate"
    extra = (f' type="{transform}"' if transform else "") + (' calcMode="discrete"' if discrete else "")
    return (f'<{tag} attributeName="{attr}"{extra} values="{";".join(str(v) for _, v in pts)}" '
            f'keyTimes="{";".join(f"{k:.5f}" for k in keys)}" dur="{T:.3f}s" repeatCount="indefinite"/>')


def f2(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def cell_xy(w, d):
    return X0 + w * STEP + CS / 2, Y0 + d * STEP + CS / 2


# ───────────────────────────── the plan ─────────────────────────────
def random_areas(rng):
    """Blast sites scattered over the grid; each lights one to four cells of its 3×3 area."""
    lit, areas = set(), []
    for _ in range(5000):
        if len(areas) == BLASTS:
            break
        w, d = rng.randrange(1, WEEKS - 1), rng.randrange(7)
        if any(abs(w - a) < 3 and abs(d - b) < 2 for (a, b), _ in areas):
            continue
        near = [(a, b) for a in (w - 1, w, w + 1) for b in (d - 1, d, d + 1) if 0 <= b < 7 and (a, b) != (w, d) and (a, b) not in lit]
        rng.shuffle(near)
        members = [(w, d)] + near[:rng.choice((0, 1, 2, 2, 3, 3))]
        lit |= set(members)
        areas.append(((w, d), {c: rng.choices((1, 2, 3, 4), (4, 3, 2, 1))[0] for c in members}))
    return areas


def stand(centre, side):
    """Where Goku stands to hit centre while facing side (+1 right, -1 left)."""
    cx, cy = cell_xy(*centre)
    hx = cx - side * REACH
    return hx - side * HAND_X, cy, hx


def plan(areas, rng):
    """Hop between blast sites in a random order (never too far at once) and lay out the timeline."""
    pos = (X0 + 30, Y0 + 3 * STEP + CS / 2)
    t, facing = INTRO, 1
    segs = [(0, INTRO, "idle", 1, pos, pos)]
    blasts = []
    todo = list(areas)
    while todo:
        options = []
        for i, (centre, _) in enumerate(todo):
            sides = [(math.dist(pos, stand(centre, side)[:2]), i, side) for side in (1, -1)
                     if 32 <= stand(centre, side)[0] <= W - 32]  # stay inside the panel
            if sides:
                options.append(min(sides))
        dist, i, side = rng.choice([o for o in options if o[0] < 360] or [min(options)])
        centre, members = todo.pop(i)
        gx, gy, hx = stand(centre, side)
        if dist > 1:
            run = .08 + dist / SPEED
            if abs(gx - pos[0]) > 2:
                facing = 1 if gx > pos[0] else -1
            segs.append((t, t + run, "run", facing, pos, (gx, gy)))
            t += run
        pos, facing = (gx, gy), side
        segs.append((t, t + CHARGE, "charge", side, pos, pos))
        segs.append((t + CHARGE, t + CHARGE + EXTEND + HOLD + FADE, "fire", side, pos, pos))
        fire = t + CHARGE
        impact = fire + EXTEND
        blasts.append({"side": side, "hx": hx, "y": gy, "centre": cell_xy(*centre), "charge": t, "fire": fire,
                       "impact": impact, "end": impact + HOLD, "reveal": {c: (impact + .035 * (abs(c[0] - centre[0]) + abs(c[1] - centre[1])), lv) for c, lv in members.items()}})
        t = fire + EXTEND + HOLD + FADE
    segs.append((t, t + VICTORY + RESET, "win", facing, pos, pos))
    return segs, blasts, t + VICTORY + RESET


# ───────────────────────────── rendering ─────────────────────────────
def sprite_defs():
    """Goku's frames and the pixel Kamehameha pieces, defined once and placed with <use>."""
    fr = gs.frames()
    out = [f'<g id="g-{n}">{gs.to_svg(fr[n], PX, -gs.W / 2 * PX, -gs.HANDS[1] * PX)}</g>' for n in ("run1", "run2", "charge", "fire", "win")]

    def centred(name, rows):
        return f'<g id="{name}">{gs.to_svg(rows, PX, -len(rows[0]) / 2 * PX, -len(rows) / 2 * PX)}</g>'
    beam = gs.beam(BEAM_LEN)
    out.append(f'<g id="k-beam">{gs.to_svg(beam, PX, 0, -len(beam) / 2 * PX)}</g>')
    out.append(AURA_DEFS)
    out += [centred("k-head1", gs.blob(7, 9, 0)), centred("k-head2", gs.blob(7, 9, .35)),
            centred("k-orb1", gs.blob(3)), centred("k-orb2", gs.blob(4, 7)),
            centred("k-burst1", gs.burst(7)), centred("k-burst2", gs.burst(11)), centred("k-ring", gs.burst(14, True))]
    return "".join(out)


AURA_DEFS = (
    # a cyan glow hugging Goku's silhouette while he runs and stands, flickering like a ki aura
    '<filter id="aura" x="-60%" y="-40%" width="220%" height="180%">'
    '<feFlood flood-color="#22d3ee" flood-opacity=".8" result="c">'
    '<animate attributeName="flood-opacity" values=".5;.95;.5" dur=".3s" repeatCount="indefinite"/></feFlood>'
    '<feComposite in="c" in2="SourceAlpha" operator="in" result="sil"/>'
    '<feMorphology in="sil" operator="dilate" radius="1.6" result="fat"/>'
    '<feGaussianBlur in="fat" stdDeviation="3.2" result="glow"/>'
    '<feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    # a soft bloom for the beam, the ki ball and the explosions
    '<filter id="kiglow" x="-50%" y="-120%" width="200%" height="340%">'
    '<feGaussianBlur in="SourceGraphic" stdDeviation="2.6" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
)


def flicker(a, b, period=".24s"):
    """Two pieces swapping back and forth forever: a run cycle, a crackling ki ball."""
    anim = '<animate attributeName="opacity" values="{}" dur="' + period + '" calcMode="discrete" repeatCount="indefinite"/>'
    return (f'<g>{anim.format("1;0")}<use xlink:href="#{a}"/></g>'
            f'<g opacity="0">{anim.format("0;1")}<use xlink:href="#{b}"/></g>')


_r = random.Random(11)
SPARKS = [(_r.uniform(-20, 18), _r.choice((2, 2.5, 3)), _r.choice(("#67e8f9", "#a5f3fc", "#22d3ee")),
           _r.uniform(.8, 1.4), _r.uniform(0, 1.4)) for _ in range(12)]


def goku(segs, T):
    pos = []
    for t0, t1, *_, a, b in segs:
        pos += [(t0, f"{f2(a[0])} {f2(a[1])}"), (t1, f"{f2(b[0])} {f2(b[1])}")]
    facing = [(t0, f"{side} 1") for t0, _, _, side, *_ in segs]
    teleport = [(0, 0), (.08, 1), (.14, .25), (.22, 1), (T - .62, 1), (T - .56, .25), (T - .5, 1), (T - .42, 0)]

    def state(name, body):
        pts = [(t0, 1 if s == name else 0) for t0, _, s, *_ in segs]
        return f'<g opacity="0">{animate("opacity", pts, T, discrete=True)}{body}</g>'

    top, bot = -gs.HANDS[1] * PX - 14, (gs.H - gs.HANDS[1]) * PX + 4
    turn = animate("transform", facing, T, discrete=True, transform="scale")
    sparks = "".join(
        f'<rect x="{f2(x)}" y="0" width="{f2(sz)}" height="{f2(sz)}" fill="{c}" opacity="0">'
        f'<animate attributeName="y" values="{f2(bot - 6)};{f2(top + 6)}" dur="{d:.2f}s" begin="{b0:.2f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;.95;0" dur="{d:.2f}s" begin="{b0:.2f}s" repeatCount="indefinite"/></rect>'
        for x, sz, c, d, b0 in SPARKS)
    return (f'<g>{animate("transform", pos, T, transform="translate")}{animate("opacity", teleport, T)}'
            f'<ellipse cx="0" cy="{f2((gs.H - gs.HANDS[1]) * PX + .5)}" rx="{f2(11 * PX)}" ry="{f2(2.2 * PX)}" fill="{INK}" opacity=".16"/>'
            f'<g filter="url(#aura)">{turn}'
            + state("idle", '<use xlink:href="#g-win"/>')
            + state("run", flicker("g-run1", "g-run2", ".26s"))
            + state("win", '<use xlink:href="#g-win"/>')
            + f'</g><g>{turn}'
            + state("charge", '<use xlink:href="#g-charge"/>')
            + state("fire", '<use xlink:href="#g-fire"/>')
            + f'</g><g shape-rendering="auto">{sparks}</g></g>')


def blast(b, T, i):
    side, hx, y = b["side"], b["hx"], b["y"]
    length = abs(b["centre"][0] - hx)
    cx, cy = b["centre"]
    ch_x = hx + side * ((gs.CHARGE_HANDS[0] - gs.W / 2) * PX - HAND_X)
    ch_y = y + (gs.CHARGE_HANDS[1] - gs.HANDS[1]) * PX
    show = [(0, 0), (b["fire"], 0), (b["fire"] + .01, 1), (b["end"], 1), (b["end"] + FADE, 0)]
    imp = b["impact"]

    def blink(t0, t1):
        return animate("opacity", [(0, 0), (t0, 1), (t1, 0)], T, discrete=True)
    orb = (
        # the ki ball crackling in his cupped hands while Goku charges (drawn over him)
        f'<g transform="translate({f2(ch_x)} {f2(ch_y)})" opacity="0" filter="url(#kiglow)">'
        + animate("opacity", [(0, 0), (b["charge"], 0), (b["charge"] + .01, 1), (b["fire"], 1), (b["fire"] + .01, 0)], T)
        + flicker("k-orb1", "k-orb2", ".1s") + "</g>")
    out = [
        # the beam: revealed pixel by pixel behind its head, drawn facing right and mirrored for left-facing blasts
        f'<g transform="translate({f2(hx)} {f2(y)}) scale({side} 1)" opacity="0" filter="url(#kiglow)">{animate("opacity", show, T)}'
        f'<clipPath id="kc{i}"><rect x="-2" y="-12" width="0" height="24">'
        + animate("width", [(0, 0), (b["fire"], 0), (imp, f2(length + 2))], T) + "</rect></clipPath>"
        f'<g clip-path="url(#kc{i})"><use xlink:href="#k-beam"/></g>'
        f'<g>{animate("transform", [(0, "0 0"), (b["fire"], "0 0"), (imp, f"{f2(length)} 0")], T, transform="translate")}'
        + flicker("k-head1", "k-head2", ".12s") + "</g></g>",
        # the explosion over the damage area: flash, bigger flash, ring of sparks
        f'<g transform="translate({f2(cx)} {f2(cy)})" filter="url(#kiglow)">'
        f'<use xlink:href="#k-burst1" opacity="0">{blink(imp, imp + .08)}</use>'
        f'<use xlink:href="#k-burst2" opacity="0">{blink(imp + .08, imp + .2)}</use>'
        f'<use xlink:href="#k-ring" opacity="0">{blink(imp + .2, imp + .34)}</use></g>',
    ]
    if i == 0:
        gx = min(max(hx - side * HAND_X, 90), W - 90)
        out.append(f'<text x="{f2(gx)}" y="{f2(y - gs.HANDS[1] * PX - 8)}" text-anchor="middle" font-family="{INTER}" font-weight="700" '
                   f'font-size="11" letter-spacing="1" fill="#1d4ed8" opacity="0">KA-ME-HA-ME-HA!'
                   + animate("opacity", [(0, 0), (b["charge"], 0), (b["charge"] + .08, 1), (b["end"] + .5, 1), (b["end"] + .8, 0)], T) + "</text>")
    return "".join(out), orb


def render(cal):
    now = datetime.now(timezone.utc)
    rng = random.Random(f"{now.date()}-{now.hour // 12}")   # a new battle every build
    segs, blasts, T = plan(random_areas(rng), rng)
    reveal = {c: v for b in blasts for c, v in b["reveal"].items()}
    fx = [blast(b, T, i) for i, b in enumerate(blasts)]

    cells = []
    for w in range(WEEKS):
        for d in range(7):
            x, y = X0 + w * STEP, Y0 + d * STEP
            if (w, d) in reveal:
                t, lv = reveal[(w, d)]
                g = GREENS[lv]
                fill = animate("fill", [(0, GREENS[0]), (t, GREENS[0]), (t + .05, FLASH), (t + .3, g), (T - RESET, g), (T - RESET / 2, GREENS[0])], T)
                cells.append(f'<rect x="{x}" y="{y}" width="{CS}" height="{CS}" rx="3" fill="{GREENS[0]}">{fill}</rect>')
            else:
                cells.append(f'<rect x="{x}" y="{y}" width="{CS}" height="{CS}" rx="3" fill="{GREENS[0]}"/>')
    total = cal["totalContributions"]
    css_path = os.path.join(HERE, "activity-fonts.css")
    fonts = f"<style>{open(css_path).read()}</style>" if os.path.exists(css_path) else ""
    icon = ('<svg x="36" y="24" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#0f172a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Training Ground: a pixel-art Goku charges up in a cyan aura and fires Kamehameha blasts across a decorative grid. {total:,} GitHub contributions in the last year.">
<title>Training Ground</title>
<defs>{fonts}<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  {sprite_defs()}
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="#fff"/>
<rect x="36" y="0" width="{W - 72}" height="1" fill="{LINE}"/>
{icon}
<text x="78" y="47" font-family="{INTER}" font-weight="700" font-size="22" fill="{INK}">Training Ground</text>
<text x="988" y="46" text-anchor="end" font-family="{INTER}" font-size="12" fill="{MUTED}"><tspan font-weight="600" fill="{INK2}">{total:,}</tspan> contributions in the last year</text>
{"".join(cells)}
<g shape-rendering="crispEdges">{"".join(under for under, _ in fx)}
{goku(segs, T)}
{"".join(over for _, over in fx)}</g>
</g>
</svg>
'''


if __name__ == "__main__":
    login, out = sys.argv[1], sys.argv[2]
    cal = mock() if login == "--mock" else fetch(login, os.environ["GITHUB_TOKEN"])
    svg = render(cal)
    ElementTree.fromstring(svg)  # GitHub only renders well-formed XML
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out} ({len(svg) / 1024:.0f} KB)")
