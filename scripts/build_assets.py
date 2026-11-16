"""Builds the static, ink-wash themed SVG panels for the krizz711 profile README.

    pip install fonttools brotli pillow
    npm i @fontsource/kaushan-script @fontsource/caveat @fontsource/jetbrains-mono \
          @fontsource/inter devicon simple-icons
    python scripts/build_assets.py --node-modules path/to/node_modules --out assets/ [--only hero]

Fonts are subset and embedded as base64 WOFF2, so every panel renders identically
inside a GitHub README. The hero's ink landscape and falling leaves are drawn in SVG,
with no embedded artwork.
The activity panel is built separately by scripts/build_activity.py.
"""
import argparse
import base64
import io
import json
import os
import re
from xml.etree import ElementTree
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

INK, INK2, MUTED, LINE, NAVY = "#0f172a", "#1f2937", "#6b7280", "#e5e7eb", "#1e293b"
ASCII = "".join(chr(c) for c in range(32, 127)) + "“”‘’—–|·→↑↓…"

NM = None  # node_modules path, set in main()


# ───────────────────────────── fonts ─────────────────────────────
def font_b64(path, text):
    font = TTFont(path)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def font_css(specs):
    """specs: list of (family, weight, file-relative-to-fontsource, text)."""
    rules = []
    for fam, weight, rel, text in specs:
        b64 = font_b64(os.path.join(NM, "@fontsource", rel), text)
        rules.append(f"@font-face{{font-family:'{fam}';font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "<style>" + "".join(rules) + "</style>"


INTER = "'Inter','Segoe UI',Helvetica,Arial,sans-serif"
JB = "'JetBrains Mono',Consolas,'Liberation Mono',monospace"
KAUSHAN = "'Kaushan Script',cursive"
CAVEAT = "'Caveat',cursive"


def std_fonts(extra=()):
    base = [("Inter", 400, "inter/files/inter-latin-400-normal.woff2", ASCII),
            ("Inter", 600, "inter/files/inter-latin-600-normal.woff2", ASCII),
            ("Inter", 700, "inter/files/inter-latin-700-normal.woff2", ASCII),
            ("JetBrains Mono", 400, "jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2", ASCII),
            ("JetBrains Mono", 500, "jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2", ASCII)]
    return font_css(base + list(extra))


# ───────────────────────────── icons ─────────────────────────────
_SI = None


def simple_icon(slug, x, y, size, color=None):
    global _SI
    if _SI is None:
        path = os.path.join(NM, "simple-icons/data/simple-icons.json")  # simple-icons >= 14
        if not os.path.exists(path):
            path = os.path.join(NM, "simple-icons/_data/simple-icons.json")
        data = json.load(open(path, encoding="utf-8"))
        data = data["icons"] if isinstance(data, dict) else data
        _SI = {i.get("slug") or re.sub(r"[^a-z0-9]", "", i["title"].lower().replace("+", "plus").replace(".", "dot")): i["hex"] for i in data}
    svg = open(os.path.join(NM, f"simple-icons/icons/{slug}.svg")).read()
    d = re.search(r'<path d="([^"]+)"', svg).group(1)
    col = color or "#" + _SI.get(slug, "111827")
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24"><path d="{d}" fill="{col}"/></svg>'


def devicon(name, x, y, size, variant="original"):
    svg = open(os.path.join(NM, f"devicon/icons/{name}/{name}-{variant}.svg")).read()
    inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", svg, flags=re.S)
    pre = re.sub(r"[^a-z]", "", name)
    inner = re.sub(r'id="([^"]+)"', lambda m: f'id="{pre}-{m.group(1)}"', inner)
    inner = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{pre}-{m.group(1)})', inner)
    inner = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{pre}-{m.group(1)}"', inner)
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 128 128">{inner}</svg>'


def line_icon(kind, x, y, size=22, color=INK2, sw=1.8):
    """Small hand-drawn line icons on a 24×24 grid."""
    p = {
        "pin": '<path d="M12 21s-6-5.6-6-11a6 6 0 0 1 12 0c0 5.4-6 11-6 11z"/><circle cx="12" cy="10" r="2.2" fill="currentColor"/>',
        "cap": '<path d="M2 9l10-5 10 5-10 5z" fill="currentColor"/><path d="M6 11v4.5c0 1.5 2.7 3 6 3s6-1.5 6-3V11"/><path d="M21 9v5"/>',
        "brain": '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 3 3 2 2 0 0 0 3-1.7V5.7A2 2 0 0 0 9 4z"/><path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-3 3 2 2 0 0 1-3-1.7"/><path d="M8 9h2M8 14h2M14 9h2M14 14h2"/>',
        "repo": '<rect x="4" y="3" width="15" height="18" rx="2"/><path d="M8 3v18"/><path d="M11 7h5M11 11h5"/>',
        "paper": '<path d="M6 2h9l4 4v16H6z"/><path d="M15 2v4h4"/><path d="M9 11h7M9 15h7M9 19h4"/>',
        "trophy": '<path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4"/><path d="M12 13v4M8 21h8M9 17h6v4H9z"/>',
        "stack": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7 3v18"/>',
        "skills": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M7 9h5M7 13h10M15 9h2"/><path d="M3 9h0"/>',
        "activity": '<circle cx="9" cy="9" r="5"/><circle cx="16" cy="14" r="5"/><circle cx="9" cy="17" r="3"/>',
        "commit": '<circle cx="12" cy="12" r="3.5"/><path d="M3 12h5.5M15.5 12H21"/>',
        "pr": '<circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M6 8.5v7M18 15.5V9a3 3 0 0 0-3-3h-4"/><path d="M13 3.5 10.5 6 13 8.5"/>',
        "issue": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/>',
        "mail": '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
        "db": '<ellipse cx="12" cy="5.5" rx="7.5" ry="3"/><path d="M4.5 5.5v13c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3v-13"/><path d="M4.5 12c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3"/>',
        "chart": '<path d="M3 21h18"/><rect x="5" y="12" width="3" height="7" fill="currentColor"/><rect x="10.5" y="8" width="3" height="11" fill="currentColor"/><rect x="16" y="4" width="3" height="15" fill="currentColor"/>',
        "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/>',
        "chat": '<path d="M4 5h16v11H9l-5 4z"/><circle cx="9" cy="10.5" r="1" fill="currentColor"/><circle cx="12" cy="10.5" r="1" fill="currentColor"/><circle cx="15" cy="10.5" r="1" fill="currentColor"/>',
        "code": '<path d="m8 7-5 5 5 5M16 7l5 5-5 5M13.5 4l-3 16"/>',
        "llm": '<rect x="4" y="4" width="16" height="16" rx="4"/><path d="M12 7.5v9M7.5 12h9M9 9l6 6M15 9l-6 6"/>',
        "diffusion": '<circle cx="16" cy="12" r="5.5"/>' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="currentColor" stroke="none"/>'
                                                                    for x, y, r in ((3, 4, 1.4), (7.5, 3, 1.1), (4.5, 9, 1.5), (8.5, 7.5, 1.1), (2.8, 14, 1.2),
                                                                                    (7, 12.5, 1.4), (4.5, 19.5, 1.4), (8.5, 17.5, 1.1))),
        "quant": '<path d="M3 21 21 3" opacity=".35"/><path d="M3 20h4.5v-4.5H12V11h4.5V6.5H21"/>',
        "lora": '<rect x="3" y="3" width="4" height="18" rx="1"/><rect x="10" y="3" width="11" height="4" rx="1"/><rect x="10" y="10" width="11" height="11" rx="1" stroke-dasharray="2 2"/>',
        "rag": '<path d="M12 21H5V3h8l4 4v4"/><path d="M13 3v4h4"/><path d="M8 9h4M8 13h3"/><circle cx="16.5" cy="16.5" r="3.5"/><path d="m19 19 2.5 2.5"/>',
        "scale": '<rect x="2.5" y="14" width="6" height="6" rx="1.2"/><rect x="10.5" y="14" width="6" height="6" rx="1.2" stroke-dasharray="2 1.6"/><path d="M19.5 3v18M16.5 6l3-3 3 3M16.5 18l3 3 3-3"/>',
    }[kind]
    return (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" color="{color}">{p}</svg>')


def brush(x1, y1, x2, y2, begin, width=4, color=INK, dur=.8):
    """A tapered brush stroke that draws itself in."""
    mx, my = (x1 + x2) / 2, min(y1, y2) - 4
    L = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5) + 20
    return (f'<path d="M{x1},{y1} Q{mx:.0f},{my:.0f} {x2},{y2}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
            f'stroke-dasharray="{L}" stroke-dashoffset="{L}"><animate attributeName="stroke-dashoffset" from="{L}" to="0" begin="{begin}s" dur="{dur}s" fill="freeze"/></path>'
            f'<path d="M{x1+8},{y1+3} Q{mx:.0f},{my+3:.0f} {x2-10},{y2+1}" fill="none" stroke="{color}" stroke-width="{width*.45:.1f}" stroke-linecap="round" opacity=".55" '
            f'stroke-dasharray="{L}" stroke-dashoffset="{L}"><animate attributeName="stroke-dashoffset" from="{L}" to="0" begin="{begin+.15:.2f}s" dur="{dur}s" fill="freeze"/></path>')


def reveal(uid, x, y, w, h, begin, dur):
    return (f'<clipPath id="{uid}"><rect x="{x}" y="{y}" height="{h}" width="0">'
            f'<animate attributeName="width" from="0" to="{w}" begin="{begin}s" dur="{dur}s" fill="freeze" calcMode="spline" keySplines=".35 0 .25 1" keyTimes="0;1"/></rect></clipPath>')


def fade_in(begin, dur=.6, dy=8):
    return (f'<animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="{dur}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 {dy}" to="0 0" begin="{begin}s" dur="{dur}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/>')


# ───────────────────────────── hero ─────────────────────────────
LEAF = "M0,-9 C5,-6 6,3 0,9 C-6,3 -5,-6 0,-9 Z"
VEIN = "M0,-7.5 L0,7.5"


def falling_leaves(H):
    """Slow ink-wash leaves drifting down the banner, fainter over the text column."""
    specs = [  # x start, sideways drift, seconds per fall, phase, scale, colour, peak opacity
        (600, 60, 13, -2, 1.0, "#1e3a8a", .45), (680, -40, 16, -9, .8, "#334155", .40),
        (760, 50, 12, -5, 1.15, "#b45309", .42), (840, -60, 15, -12, .9, "#1e3a8a", .38),
        (900, 40, 14, -3.5, .75, "#475569", .42), (960, -50, 17, -7, 1.05, "#3b4a7a", .40),
        (1000, -80, 13.5, -10.5, .85, "#b45309", .32), (560, 70, 18, -14, .7, "#475569", .30),
        (120, 50, 19, -6, .7, "#64748b", .16), (300, -40, 21, -15, .6, "#64748b", .14),
        (450, 60, 20, -1, .65, "#94a3b8", .18)]
    out = []
    for x, drift, dur, begin, s, col, op in specs:
        path = f"M{x},-24 C{x + drift * .8:.0f},{H * .3:.0f} {x - drift * .5:.0f},{H * .65:.0f} {x + drift:.0f},{H + 24}"
        spin = 200 if drift > 0 else -200
        out.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" values="0;{op};{op};0" keyTimes="0;.12;.85;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animateMotion path="{path}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<g transform="scale({s * 1.4:.2f})"><g>'
            f'<animateTransform attributeName="transform" type="rotate" values="0;{spin};{spin * 2}" dur="{dur * .9:.1f}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<path d="{LEAF}" fill="{col}"/><path d="{VEIN}" stroke="#fff" stroke-width=".7" opacity=".55"/>'
            f'</g></g></g>')
    return "".join(out)


def ink_landscape(W, H):
    """Layered sumi-e ridges with drifting mist and a soft sun, fading into the white text column."""
    ridges = [
        ("M540,300 C600,240 640,252 690,206 C730,172 762,192 802,150 C842,114 880,150 922,120 C962,94 992,120 1024,104 L1024,372 L540,372 Z", "ra", .20),
        ("M560,332 C622,282 662,300 722,250 C772,210 812,240 862,200 C912,166 952,210 1024,180 L1024,372 L560,372 Z", "rb", .32),
        ("M610,372 C660,332 706,346 764,302 C822,260 872,300 932,270 C972,250 1000,262 1024,256 L1024,372 Z", "rc", .55)]
    grads, paths = [], []
    for d, gid, op in ridges:
        grads.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1e293b" stop-opacity="{op}"/>'
                     f'<stop offset="1" stop-color="#1e293b" stop-opacity="0"/></linearGradient>')
        paths.append(f'<path d="{d}" fill="url(#{gid})"/>')
    mist = []
    for i, (y, w, dur) in enumerate([(250, 280, 26), (300, 360, 32), (215, 220, 22)]):
        mist.append(f'<ellipse cx="0" cy="{y}" rx="{w / 2:.0f}" ry="{12 + i * 4}" fill="#fff" opacity=".6" filter="url(#mistblur)">'
                    f'<animate attributeName="cx" values="{520 - w / 2:.0f};{W + w / 2:.0f}" dur="{dur}s" begin="-{i * 8}s" repeatCount="indefinite"/></ellipse>')
    sun = ('<circle cx="900" cy="86" r="34" fill="#e0e7ff"><animate attributeName="opacity" values=".55;.9;.55" dur="8s" repeatCount="indefinite"/></circle>'
           '<circle cx="900" cy="86" r="46" fill="none" stroke="#c7d2fe" stroke-width="1.2" opacity=".6"/>')
    defs = ("".join(grads) + '<filter id="mistblur" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>'
            '<linearGradient id="fadeL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    # back ridge, mist, mid ridge, mist, front ridge, mist; then fade the left edge into the text column
    body = sun + paths[0] + mist[2] + paths[1] + mist[0] + paths[2] + mist[1] + f'<rect x="500" y="0" width="160" height="{H}" fill="url(#fadeL)"/>'
    return defs, body


def hero():
    W, H = 1024, 372
    name = "Munal Singh"
    fonts = std_fonts([("Kaushan Script", 400, "kaushan-script/files/kaushan-script-latin-400-normal.woff2", name),
                       ("Caveat", 500, "caveat/files/caveat-latin-500-normal.woff2", ASCII)])
    tagline = ["Building intelligent systems, one line of code at a time.",
               "Passionate about AI/ML, data science, maths, physics and",
               "creating real-world impact through technology."]
    tag_svg = []
    t0 = 1.6
    for i, line in enumerate(tagline):
        y = 226 + i * 21
        w = len(line) * 7.9 + 6
        d = len(line) * .018
        tag_svg.append(reveal(f"tl{i}", 36, y - 15, w, 22, round(t0, 2), round(d, 2)) +
                       f'<text x="36" y="{y}" font-family="{JB}" font-size="13" fill="{INK2}" clip-path="url(#tl{i})">{escape(line)}</text>')
        t0 += d + .05
    land_defs, land = ink_landscape(W, H)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Munal Singh: AI/ML Engineer, Data Science Enthusiast, Problem Solver.">
<title>Munal Singh: AI/ML Engineer · Data Science Enthusiast · Problem Solver</title>
<defs>{fonts}
  {land_defs}
  {reveal("nm", 30, 60, 480, 100, .3, 1.6)}
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="#fff"/>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="1.6s" fill="freeze"/>{land}</g>
{falling_leaves(H)}
{simple_icon("github", 36, 26, 38, INK)}
<text x="96" y="50" font-family="{JB}" font-size="12" letter-spacing="3" fill="{MUTED}">CODE  /  BUILD  /  LEARN  /  GROW</text>
<g clip-path="url(#nm)">
  <text x="36" y="136" font-family="{KAUSHAN}" font-size="64" fill="{INK}">{name}</text>
  <path d="M404,120 l14,-22 l9,12 l7,-9 l15,19" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M414,106 l4,-4 l4,5" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>
</g>
<g opacity="0">{fade_in(1.2)}
  <text x="36" y="178" font-family="{JB}" font-weight="500" font-size="13.5" fill="{INK}" xml:space="preserve">AI/ML Engineer  |  Data Science Enthusiast  |  Problem Solver</text>
</g>
{"".join(tag_svg)}
<g opacity="0">{fade_in(2.7)}
  <text x="36" y="318" font-family="{CAVEAT}" font-weight="500" font-size="22" fill="{INK2}">“Better than yesterday.”</text>
</g>
{brush(40, 337, 118, 332, 2.9, 3)}
</g>
</svg>
'''


# ───────────────────────────── skills ─────────────────────────────
SKILLS = [
    # deep learning research
    [("Python", "dev:python"), ("PyTorch", "dev:pytorch"), ("Hugging Face", "si:huggingface:#FFB000"),
     ("Diffusion Models", "li:diffusion:#db2777"), ("Quantization", "li:quant:#0891b2"), ("Computer Vision", "li:eye:#4f46e5")],
    # LLM systems and agents
    [("vLLM", "si:vllm"), ("LoRA Fine-Tuning", "li:lora:#ea580c"), ("Google ADK", "si:google:#4285F4"),
     ("MCP", "si:modelcontextprotocol:#111827"), ("RAG", "li:rag:#16a34a"), ("MLflow", "si:mlflow")],
    # backend and data
    [("Go", "dev:go"), ("FastAPI", "dev:fastapi"), ("Kafka", "dev:apachekafka"),
     ("Redis", "dev:redis"), ("PostgreSQL", "dev:postgresql"), ("Docker", "dev:docker")],
    # cloud-native infrastructure
    [("Kubernetes", "dev:kubernetes"), ("Helm", "dev:helm"), ("KEDA", "li:scale:#2563eb"),
     ("Prometheus", "dev:prometheus"), ("Grafana", "dev:grafana"), ("AWS", "dev:amazonwebservices:original-wordmark")],
]
_ADV = None


def text_width(s, size):
    """Advance width of s in Inter 400, so every pill fits its label exactly."""
    global _ADV
    if _ADV is None:
        f = TTFont(os.path.join(NM, "@fontsource/inter/files/inter-latin-400-normal.woff2"))
        _ADV = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    cmap, hmtx, upm = _ADV
    return sum(hmtx[cmap[ord(c)]][0] for c in s) * size / upm


def icon_from(spec, x, y, size):
    kind, *rest = spec.split(":")
    if kind == "dev":
        return devicon(rest[0], x, y, size, rest[1] if len(rest) > 1 else "original")
    if kind == "si":
        return simple_icon(rest[0], x, y, size, rest[1] if len(rest) > 1 else None)
    return line_icon(rest[0], x, y, size, rest[1], 2)


def skills():
    W, H = 1024, 88 + 60 * len(SKILLS)
    rows = []
    k = 0
    for r, row in enumerate(SKILLS):
        y = 78 + r * 60
        natural = [text_width(lab, 13.5) + 72 for lab, _ in row]
        gap = 12
        extra = (W - 72 - sum(natural) - gap * (len(row) - 1)) / len(row)
        x = 36
        for (lab, spec), nw in zip(row, natural):
            w = nw + extra
            beg = .2 + k * .06
            rows.append(f'<g opacity="0">{fade_in(beg, .5, 10)}'
                        f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="46" rx="10" fill="#fff" stroke="{LINE}"/>'
                        + icon_from(spec, round(x + 18), y + 11, 24) +
                        f'<text x="{x + 54:.1f}" y="{y + 28}" font-family="{INTER}" font-size="13.5" fill="{INK2}">{escape(lab)}</text>'
                        f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="46" rx="10" fill="url(#shine)" opacity="0">'
                        f'<animate attributeName="opacity" values="0;1;0" dur="1.2s" begin="{3 + k * .25:.2f}s;{3 + k*.25 + 8:.2f}s" /></rect></g>')
            x += w + gap
            k += 1
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Skills and technologies: {escape(", ".join(l for row in SKILLS for l, _ in row))}">
<title>Skills &amp; Technologies</title>
<defs>{std_fonts()}
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#eef2ff" stop-opacity="0"/><stop offset=".5" stop-color="#e0e7ff" stop-opacity=".9"/><stop offset="1" stop-color="#eef2ff" stop-opacity="0"/></linearGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="#fff"/>
<rect x="36" y="0" width="{W-72}" height="1" fill="{LINE}"/>
{line_icon("skills", 36, 24, 28, INK, 2)}
<text x="78" y="47" font-family="{INTER}" font-weight="700" font-size="22" fill="{INK}">Skills &amp; Technologies</text>
{"".join(rows)}
</g>
</svg>
'''


# ───────────────────────────── connect badges ─────────────────────────────
# LinkedIn is no longer in simple-icons (removed at LinkedIn's request), so its "in" mark is drawn here.
LINKEDIN_IN = ('<rect x="2" y="2" width="20" height="20" rx="3.6" fill="#0A66C2"/>'
               '<circle cx="7.4" cy="7.2" r="1.6" fill="#fff"/>'
               '<rect x="6.1" y="9.6" width="2.6" height="8.4" rx=".4" fill="#fff"/>'
               '<path d="M10.6,9.6h2.5v1.2c.5-.9 1.5-1.45 2.75-1.45 2.05 0 2.95 1.3 2.95 3.5V18h-2.6v-4.6'
               'c0-1.1-.4-1.75-1.35-1.75-1.05 0-1.65.75-1.65 1.9V18h-2.6Z" fill="#fff"/>')

# simple-icons' Kaggle icon is the full wordmark, unreadable at 20 px, so its blue "k" is drawn too.
KAGGLE_K = ('<rect x="5.2" y="2" width="3.6" height="20" rx="1.2" fill="#20BEFF"/>'
            '<path d="M18.2,8.6 L10.6,15.2 M12.9,13.4 L18.6,21" fill="none" stroke="#20BEFF" stroke-width="3.4" '
            'stroke-linecap="round" stroke-linejoin="round"/>')
DRAWN = {"kaggle": KAGGLE_K, "linkedin": LINKEDIN_IN}

CONNECT = [  # file name, label, simple-icons slug (None = drawn above, keyed by file name)
    ("kaggle", "Kaggle", None),
    ("linkedin", "LinkedIn", None),
    ("leetcode", "LeetCode", "leetcode"),
    ("email", "Email", "gmail"),
    ("chess", "Chess.com", "chessdotcom"),
]


def connect_badge(fname, label, slug):
    """A white pill with the brand's own logo, sized to its label."""
    size, pad_l, gap, pad_r, H = 14, 14, 10, 18, 40
    W = round(pad_l + 20 + gap + text_width(label, size) * 1.06 + pad_r)
    icon = (simple_icon(slug, pad_l, 10, 20) if slug else
            f'<svg x="{pad_l}" y="10" width="20" height="20" viewBox="0 0 24 24">{DRAWN[fname]}</svg>')
    fonts = font_css([("Inter", 600, "inter/files/inter-latin-600-normal.woff2", label)])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(label)}">'
            f'<title>{escape(label)}</title><defs>{fonts}</defs>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="{(H - 1) / 2}" fill="#fff" stroke="#e5e7eb"/>'
            f'{icon}<text x="{pad_l + 20 + gap}" y="25.2" font-family="{INTER}" font-weight="600" font-size="{size}" fill="{INK}">{escape(label)}</text></svg>')


def main():
    global NM
    ap = argparse.ArgumentParser()
    ap.add_argument("--node-modules", required=True)
    ap.add_argument("--out", default="assets")
    ap.add_argument("--only", nargs="*", help="build just these panels, e.g. --only hero connect")
    a = ap.parse_args()
    NM = a.node_modules
    os.makedirs(a.out, exist_ok=True)
    for name, build in (("hero.svg", hero), ("skills.svg", skills)):
        if a.only and name[:-4] not in a.only:
            continue
        svg = build()
        # GitHub serves these as standalone images, so they must be well-formed XML
        # (an undeclared xlink: prefix renders as a broken image there, though HTML embeds forgive it).
        ElementTree.fromstring(svg)
        with open(os.path.join(a.out, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"{name}: {len(svg)/1024:.0f} KB")
    if not a.only or "connect" in a.only:
        os.makedirs(os.path.join(a.out, "connect"), exist_ok=True)
        for fname, label, slug in CONNECT:
            svg = connect_badge(fname, label, slug)
            ElementTree.fromstring(svg)
            with open(os.path.join(a.out, "connect", f"{fname}.svg"), "w", encoding="utf-8") as f:
                f.write(svg)
            print(f"connect/{fname}.svg: {len(svg)/1024:.1f} KB")


if __name__ == "__main__":
    main()
