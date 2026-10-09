"""Builds the "GitHub Activity" panel of the profile README from live data.

Runs in GitHub Actions (.github/workflows/profile-assets.yml) with the
workflow's GITHUB_TOKEN and nothing but the standard library.

    python scripts/build_activity.py <login> dist/activity.svg
    python scripts/build_activity.py --mock dist/activity.svg      # offline preview
"""
import json
import os
import random
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from xml.sax.saxutils import escape

QUERY = """
query($login: String!, $pfrom: DateTime!, $pto: DateTime!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { contributionCount date weekday } }
      }
    }
    prev: contributionsCollection(from: $pfrom, to: $pto) {
      contributionCalendar { totalContributions }
    }
  }
}
"""

INTER = "'Inter','Segoe UI',Helvetica,Arial,sans-serif"
INK, INK2, MUTED, LINE = "#0f172a", "#1f2937", "#6b7280", "#e5e7eb"
GREENS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
HERE = os.path.dirname(os.path.abspath(__file__))


def fetch(login, token):
    now = datetime.now(timezone.utc)
    variables = {"login": login,
                 "pfrom": (now - timedelta(days=730)).isoformat(),
                 "pto": (now - timedelta(days=365)).isoformat()}
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-activity"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def mock():
    rng = random.Random(5)
    start = date.today() - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    weeks, d = [], start
    while d <= date.today():
        days = []
        for _ in range(7):
            if d <= date.today():
                days.append({"contributionCount": max(0, int(rng.gauss(2.5, 3.5))), "date": d.isoformat(), "weekday": (d.weekday() + 1) % 7})
            d += timedelta(days=1)
        weeks.append({"firstDay": days[0]["date"], "contributionDays": days})
    total = sum(x["contributionCount"] for w in weeks for x in w["contributionDays"])
    return {"contributionsCollection": {"totalCommitContributions": int(total * .62), "totalPullRequestContributions": 31,
                                        "totalIssueContributions": 9,
                                        "contributionCalendar": {"totalContributions": total, "weeks": weeks}},
            "prev": {"contributionCalendar": {"totalContributions": int(total * .7)}}}


ICONS = {
    "activity": '<circle cx="9" cy="9" r="5"/><circle cx="16" cy="14" r="5"/><circle cx="9" cy="17" r="3"/>',
    "commit": '<circle cx="12" cy="12" r="3.5"/><path d="M3 12h5.5M15.5 12H21"/>',
    "pr": '<circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M6 8.5v7M18 15.5V9a3 3 0 0 0-3-3h-4"/><path d="M13 3.5 10.5 6 13 8.5"/>',
    "issue": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/>',
}


def icon(kind, x, y, size, color=INK2, sw=1.9):
    return (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" color="{color}">{ICONS[kind]}</svg>')


def fade(begin, dur=.5):
    return f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/>'


def render(u):
    W, H = 1024, 232
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = cal["weeks"][-53:]
    counts = sorted(d["contributionCount"] for w in weeks for d in w["contributionDays"] if d["contributionCount"])
    # quartile buckets, like GitHub's own graph
    q = [counts[int(len(counts) * f)] if counts else 1 for f in (.25, .5, .75)]

    def level(c):
        if c == 0:
            return 0
        return 1 + sum(c > t for t in q)
    step, cs = 11.2, 9
    x0, y0 = 82, 86
    cells, months = [], []
    last_month = None
    for wi, w in enumerate(weeks):
        x = x0 + wi * step
        m = date.fromisoformat(w["firstDay"]).strftime("%b")
        if m != last_month and wi < len(weeks) - 2:
            if last_month is not None or wi == 0:
                months.append(f'<text x="{x:.1f}" y="{y0 - 10}" font-family="{INTER}" font-size="10.5" fill="{MUTED}">{m}</text>')
            last_month = m
        for d in w["contributionDays"]:
            y = y0 + d["weekday"] * step
            lv = min(4, level(d["contributionCount"]))
            cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cs}" height="{cs}" rx="2" fill="{GREENS[lv]}" opacity="0">{fade(.2 + wi * .018, .35)}'
                         f'<title>{d["contributionCount"]} on {d["date"]}</title></rect>')
    days = "".join(f'<text x="36" y="{y0 + r * step + 8:.1f}" font-family="{INTER}" font-size="10.5" fill="{MUTED}">{n}</text>'
                   for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    legend_x = x0 + 53 * step - 5 * 12 - 60
    legend = (f'<text x="{legend_x - 6:.0f}" y="{y0 + 7*step + 22:.0f}" text-anchor="end" font-family="{INTER}" font-size="10.5" fill="{MUTED}">Less</text>'
              + "".join(f'<rect x="{legend_x + i*12:.0f}" y="{y0 + 7*step + 13:.0f}" width="{cs}" height="{cs}" rx="2" fill="{c}"/>' for i, c in enumerate(GREENS))
              + f'<text x="{legend_x + 5*12 + 4:.0f}" y="{y0 + 7*step + 22:.0f}" font-family="{INTER}" font-size="10.5" fill="{MUTED}">More</text>')
    total = cal["totalContributions"]
    prev = (u.get("prev") or {}).get("contributionCalendar", {}).get("totalContributions") or 0
    change = ""
    if prev:
        pct = round((total - prev) / prev * 100)
        up = pct >= 0
        change = (f'<text x="{720 + len(f"{total:,}") * 18 + 14}" y="113" font-family="{INTER}" font-weight="600" font-size="13" fill="{"#16a34a" if up else "#dc2626"}">'
                  f'{"↑" if up else "↓"} {abs(pct)}%</text>')
    cols = [("commit", "Commits", cc["totalCommitContributions"]), ("pr", "Pull Requests", cc["totalPullRequestContributions"]),
            ("issue", "Issues", cc["totalIssueContributions"])]
    col_svg = []
    for i, (ic, lab, val) in enumerate(cols):
        x = (716, 806, 922)[i]
        col_svg.append(f'<g opacity="0">{fade(1.3 + i * .15)}' + icon(ic, x, 160, 16) +
                       f'<text x="{x + 22}" y="173" font-family="{INTER}" font-size="11.5" fill="#374151">{lab}</text>'
                       f'<text x="{x + 22}" y="202" font-family="{INTER}" font-weight="700" font-size="18" fill="{INK}">{val:,}</text></g>')
        if i:
            col_svg.append(f'<rect x="{x - 12}" y="160" width="1" height="46" fill="{LINE}"/>')
    css_path = os.path.join(HERE, "activity-fonts.css")
    fonts = f"<style>{open(css_path).read()}</style>" if os.path.exists(css_path) else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub activity: {total:,} contributions in the last 12 months, {cc["totalCommitContributions"]:,} commits, {cc["totalPullRequestContributions"]:,} pull requests, {cc["totalIssueContributions"]:,} issues">
<title>GitHub Activity — updated {date.today().isoformat()}</title>
<defs>{fonts}<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="#fff"/>
<rect x="36" y="0" width="{W-72}" height="1" fill="{LINE}"/>
{icon("activity", 36, 24, 28, INK, 2)}
<text x="78" y="47" font-family="{INTER}" font-weight="700" font-size="22" fill="{INK}">GitHub Activity</text>
<text x="988" y="46" text-anchor="end" font-family="{INTER}" font-size="11.5" fill="{MUTED}">updated {date.today().strftime("%d %b %Y")}</text>
{"".join(months)}
{days}
{"".join(cells)}
{legend}
<g opacity="0">{fade(1.0)}
  <text x="720" y="82" font-family="{INTER}" font-size="13" fill="#374151">Total Contributions</text>
  <text x="720" y="114" font-family="{INTER}" font-weight="700" font-size="30" fill="{INK}">{total:,}</text>
  {change}
  <text x="720" y="134" font-family="{INTER}" font-size="11.5" fill="{MUTED}">(last 12 months)</text>
  <rect x="720" y="146" width="268" height="1" fill="{LINE}"/>
</g>
{"".join(col_svg)}
</g>
</svg>
'''


if __name__ == "__main__":
    login, out = sys.argv[1], sys.argv[2]
    data = mock() if login == "--mock" else fetch(login, os.environ["GITHUB_TOKEN"])
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        f.write(render(data))
    print(f"wrote {out}")
