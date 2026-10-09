"""Builds the static, ink-wash themed SVG panels for the krizz711 profile README.

    pip install fonttools brotli pillow
    npm i @fontsource/kaushan-script @fontsource/caveat @fontsource/jetbrains-mono \
          @fontsource/inter @fontsource/yuji-boku devicon simple-icons
    python scripts/build_assets.py --node-modules path/to/node_modules --art art/ --out assets/

Fonts are subset and embedded as base64 WOFF2 and the artwork is embedded as
base64 JPEG, so every panel renders identically inside a GitHub README.
The activity panel is built separately by scripts/build_activity.py.
"""
import argparse
import base64
import io
import json
import os
import re
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
YUJI = "'Yuji Boku',serif"


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


def jpeg_b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()


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
def hero(art):
    W, H = 1024, 440
    name = "Munal Singh"
    fonts = std_fonts([("Kaushan Script", 400, "kaushan-script/files/kaushan-script-latin-400-normal.woff2", name),
                       ("Caveat", 500, "caveat/files/caveat-latin-500-normal.woff2", ASCII),
                       ("Yuji Boku", 400, "yuji-boku/files/yuji-boku-japanese-400-normal.woff2", "孫悟空")])
    tagline = ["Building intelligent systems, one line of code at a time.",
               "Passionate about AI/ML, data science, maths, physics and",
               "creating real-world impact through technology."]
    tag_svg = []
    t0 = 1.6
    for i, line in enumerate(tagline):
        y = 252 + i * 21
        w = len(line) * 7.9 + 6
        d = len(line) * .018
        tag_svg.append(reveal(f"tl{i}", 36, y - 15, w, 22, round(t0, 2), round(d, 2)) +
                       f'<text x="36" y="{y}" font-family="{JB}" font-size="13" fill="{INK2}" clip-path="url(#tl{i})">{escape(line)}</text>')
        t0 += d + .05
    pills = [("brain", "AI/ML Projects", "15+"), ("repo", "Repositories", "30+"),
             ("paper", "Research", "1 paper"), ("trophy", "Competitions", "4+")]
    pill_svg = []
    for i, (ic, lab, val) in enumerate(pills):
        x = 36 + i * 146
        pill_svg.append(f'<g opacity="0">{fade_in(3.0 + i * .12)}'
                        f'<rect x="{x}" y="366" width="136" height="56" rx="12" fill="#fff" stroke="{LINE}"/>'
                        + line_icon(ic, x + 13, 382, 24) +
                        f'<text x="{x+48}" y="388" font-family="{INTER}" font-size="12" fill="#4b5563">{lab}</text>'
                        f'<text x="{x+48}" y="410" font-family="{INTER}" font-weight="600" font-size="17" fill="{INK}">{val}</text></g>')
    stack_icons = [devicon("python", 0, 0, 30), devicon("pytorch", 0, 0, 30), simple_icon("openai", 0, 0, 30, "#ffffff"),
                   line_icon("db", 0, 0, 30, "#60a5fa", 2), devicon("mongodb", 0, 0, 30)]
    stack_svg = []
    for i, ic in enumerate(stack_icons):
        x = 672 + i * 54
        ic = ic.replace('x="0" y="0"', f'x="{x}" y="386"', 1)
        stack_svg.append(f'<g opacity="0">{fade_in(3.4 + i * .1, .5, 10)}{ic}</g>')
    stack_svg.append(f'<g opacity="0">{fade_in(3.9, .5, 10)}<path d="M{672+5*54+8},401 h16 M{672+5*54+16},393 v16" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></g>')
    wisps = []
    for i, (d, op) in enumerate([("M600,300 C640,250 610,190 660,150 C700,120 690,80 740,60", .16),
                                 ("M930,320 C900,270 940,220 905,170 C880,135 915,100 890,60", .14),
                                 ("M560,180 C600,160 590,120 630,95", .12)]):
        wisps.append(f'<path d="{d}" fill="none" stroke="#3b4a7a" stroke-width="{10 - i*2}" stroke-linecap="round" opacity="{op}" stroke-dasharray="420" stroke-dashoffset="420">'
                     f'<animate attributeName="stroke-dashoffset" values="420;0;0;-420" keyTimes="0;.4;.6;1" dur="{9 + i*2}s" begin="{i*1.3}s" repeatCount="indefinite"/></path>')
    dots = []
    for i, (x, y) in enumerate([(612, 260), (640, 310), (905, 250), (940, 300), (585, 120), (880, 40), (700, 320)]):
        dots.append(f'<circle cx="{x}" cy="{y}" r="{1.6 + (i % 3)}" fill="#1e3a8a" opacity="0">'
                    f'<animate attributeName="cy" values="{y};{y-60}" dur="{5 + i % 3}s" begin="{i*.7}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values="0;.45;0" dur="{5 + i % 3}s" begin="{i*.7}s" repeatCount="indefinite"/></circle>')
    kanji = "".join(f'<g opacity="0">{fade_in(1.0 + i * .35, .9, -10)}<text x="980" y="{98 + i*50}" text-anchor="middle" font-family="{YUJI}" font-size="40" fill="{NAVY}">{c}</text></g>'
                    for i, c in enumerate("孫悟空"))
    motto = "".join(f'<g opacity="0">{fade_in(2.2 + i * .2, .6)}<text x="980" y="{236 + i*20}" text-anchor="middle" font-family="{JB}" font-size="10" letter-spacing="3" fill="#475569">{w}</text></g>'
                    for i, w in enumerate(["HIGHER", "FURTHER", "STRONGER"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Munal Singh: AI/ML Engineer, Data Science Enthusiast, Problem Solver. Himachal Pradesh, India. VIT Vellore, CSE (Data Science).">
<title>Munal Singh: AI/ML Engineer · Data Science Enthusiast · Problem Solver</title>
<defs>{fonts}
  {reveal("nm", 30, 60, 480, 100, .3, 1.6)}
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="#fff"/>
<rect x="0" y="0" width="{W}" height="{H}" fill="#f3f4fb" opacity=".0"/>
{"".join(wisps)}
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="1.4s" fill="freeze"/>
  <image x="512" y="0" width="430" height="335" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/jpeg;base64,{art}" href="data:image/jpeg;base64,{art}"/>
</g>
{"".join(dots)}
{kanji}
{motto}
{brush(944, 296, 1012, 290, 2.9, 3.2)}
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
<g opacity="0">{fade_in(1.4)}
  {line_icon("pin", 34, 199, 18, INK)}
  <text x="58" y="213" font-family="{INTER}" font-size="13.5" fill="{INK2}">Himachal Pradesh, India</text>
  <text x="222" y="213" font-family="{INTER}" font-size="13.5" fill="#d1d5db">|</text>
  {line_icon("cap", 238, 198, 19, INK)}
  <text x="264" y="213" font-family="{INTER}" font-size="13.5" fill="{INK2}">VIT Vellore</text>
  <text x="345" y="213" font-family="{INTER}" font-size="13.5" fill="#d1d5db">|</text>
  <text x="358" y="213" font-family="{INTER}" font-size="13.5" fill="{INK2}">CSE (Data Science)</text>
</g>
{"".join(tag_svg)}
<g opacity="0">{fade_in(2.7)}
  <text x="36" y="330" font-family="{CAVEAT}" font-weight="500" font-size="22" fill="{INK2}">“Better than yesterday.”</text>
</g>
{brush(40, 349, 118, 344, 2.9, 3)}
{"".join(pill_svg)}
<g opacity="0">{fade_in(3.2)}
  <rect x="652" y="356" width="336" height="68" rx="16" fill="#0f172a"/>
  <text x="672" y="377" font-family="{JB}" font-size="11.5" fill="#e5e7eb">Tech Stack I work with</text>
</g>
{"".join(stack_svg)}
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
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Skills and technologies: {escape(", ".join(l for row in SKILLS for l, _ in row))}">
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


# ───────────────────────────── footer ─────────────────────────────
def footer(art):
    W, H = 1024, 236
    BG = "#f6f7fb"
    quote = ["The strongest people", "are not those who never fall,", "but those who rise every time they do. ”"]
    fonts = std_fonts([("Caveat", 500, "caveat/files/caveat-latin-500-normal.woff2", ASCII)])
    lines = []
    for i, q in enumerate(quote):
        y = 76 + i * 38
        w = len(q) * 11.2 + 10
        lines.append(reveal(f"q{i}", 60, y - 30, w, 42, .5 + i * .9, .9) +
                     f'<text x="64" y="{y}" font-family="{CAVEAT}" font-weight="500" font-size="27" fill="{NAVY}" clip-path="url(#q{i})">{escape(q)}</text>')
    mist = []
    for i, (y, w, dur) in enumerate([(150, 260, 22), (185, 340, 28), (120, 200, 18)]):
        mist.append(f'<ellipse cx="0" cy="{y}" rx="{w/2:.0f}" ry="{14 + i*4}" fill="#fff" opacity=".55" filter="url(#blur)">'
                    f'<animate attributeName="cx" values="{300 - w/2:.0f};{780 + w/2:.0f}" dur="{dur}s" begin="-{i*7}s" repeatCount="indefinite"/></ellipse>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="“The strongest people are not those who never fall, but those who rise every time they do.” Goku. Let's connect: open to internships, collaborations and great conversations.">
<title>The strongest people are not those who never fall, but those who rise every time they do. — Goku</title>
<defs>{fonts}
  <filter id="blur" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <clipPath id="artclip"><rect x="330" y="26" width="412" height="{H-26}"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<image x="330" y="44" width="412" height="184" xlink:href="data:image/jpeg;base64,{art}" href="data:image/jpeg;base64,{art}"/>
<circle cx="640" cy="78" r="22" fill="#fff" opacity=".7"><animate attributeName="opacity" values=".45;.85;.45" dur="6s" repeatCount="indefinite"/></circle>
<g clip-path="url(#artclip)">{"".join(mist)}</g>
<text x="38" y="70" font-family="{CAVEAT}" font-weight="500" font-size="30" fill="{NAVY}" opacity="0">“<animate attributeName="opacity" from="0" to="1" begin=".3s" dur=".4s" fill="freeze"/></text>
{"".join(lines)}
<g opacity="0">{fade_in(3.3)}<text x="64" y="196" font-family="{INTER}" font-size="15" fill="{NAVY}">— Goku</text></g>
<rect x="752" y="42" width="1.2" height="150" fill="#c7cde0"/>
<g opacity="0">{fade_in(.6)}
  <text x="778" y="66" font-family="{INTER}" font-weight="600" font-size="15" letter-spacing=".8" fill="{NAVY}">Let's Connect</text>
  {simple_icon("github", 778, 84, 32, INK)}
  {line_icon("mail", 830, 84, 34, "#1e3a8a", 2)}
  <text x="778" y="150" font-family="{INTER}" font-size="13.5" fill="#334155">Open to internships, collaborations</text>
  <text x="778" y="170" font-family="{INTER}" font-size="13.5" fill="#334155">and great conversations!</text>
</g>
{brush(790, 196, 905, 190, 1.4, 3.4, "#1e3a8a")}
</g>
</svg>
'''


def main():
    global NM
    ap = argparse.ArgumentParser()
    ap.add_argument("--node-modules", required=True)
    ap.add_argument("--art", required=True, help="folder with goku_top.jpg and goku_foot.jpg")
    ap.add_argument("--out", default="assets")
    a = ap.parse_args()
    NM = a.node_modules
    os.makedirs(a.out, exist_ok=True)
    top, foot = jpeg_b64(os.path.join(a.art, "goku_top.jpg")), jpeg_b64(os.path.join(a.art, "goku_foot.jpg"))
    for name, svg in (("hero.svg", hero(top)), ("skills.svg", skills()), ("footer.svg", footer(foot))):
        with open(os.path.join(a.out, name), "w") as f:
            f.write(svg)
        print(f"{name}: {len(svg)/1024:.0f} KB")


if __name__ == "__main__":
    main()
