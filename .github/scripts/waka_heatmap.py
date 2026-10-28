"""Draws WakaTime coding time as a GitHub-style contribution graph, in blues.

Daily totals are kept in waka/days.json (date -> seconds) so the graph keeps
a full year even when the WakaTime plan only returns recent days. Each run
merges what the API returns, then writes waka/heatmap.svg (light) and
waka/heatmap-dark.svg (dark).

Needs WAKATIME_API_KEY in the environment; without it, it only redraws.
"""

import base64
import datetime as dt
import json
import os
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
DAYS_FILE = ROOT / "waka" / "days.json"
API = "https://wakatime.com/api/v1/users/current"

# GitLab-style blues: empty, then four levels.
THEMES = {
    "heatmap.svg": {
        "levels": ["#ebedf0", "#acd5f2", "#7fa8c9", "#527ba0", "#254e77"],
        "text": "#1f2328",
        "muted": "#59636e",
        "border": "#d1d9e0",
        "bg": "#ffffff",
    },
    "heatmap-dark.svg": {
        "levels": ["#151b23", "#0d3a6b", "#1a64b5", "#3d8fe6", "#8cc8ff"],
        "text": "#f0f6fc",
        "muted": "#9198a1",
        "border": "#3d444d",
        "bg": "#0d1117",
    },
}

CELL, GAP = 10, 3
STEP = CELL + GAP
LEFT, TOP, PAD = 46, 52, 16


def _get(path, key):
    token = base64.b64encode(key.encode()).decode()
    req = urllib.request.Request(
        f"{API}{path}", headers={"Authorization": f"Basic {token}"}
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def fetch(key):
    """Date -> seconds for as much history as the plan allows."""
    days = {}
    try:
        for d in _get("/insights/days/last_year", key)["data"]["days"]:
            days[d["date"]] = float(d.get("total") or 0)
        print(f"insights: {len(days)} days")
        return days
    except (urllib.error.HTTPError, KeyError, TypeError) as e:
        print(f"insights unavailable ({e}); using summaries")
    end = dt.date.today()
    start = end - dt.timedelta(days=13)
    res = _get(f"/summaries?start={start}&end={end}", key)
    for s in res["data"]:
        days[s["range"]["date"]] = float(s["grand_total"]["total_seconds"])
    print(f"summaries: {len(days)} days")
    return days


def hours(seconds):
    h, m = divmod(int(round(seconds / 60)), 60)
    return f"{h}h {m}m" if h else f"{m}m"


def render(days, theme):
    today = dt.date.today()
    # Columns are Sunday-first weeks; the last column holds today.
    last_sunday = today - dt.timedelta(days=(today.weekday() + 1) % 7)
    first = last_sunday - dt.timedelta(weeks=52)
    span = [first + dt.timedelta(days=i) for i in range((today - first).days + 1)]

    values = [days.get(d.isoformat(), 0) for d in span]
    nonzero = sorted(v for v in values if v > 0)

    def level(v):
        if v <= 0 or not nonzero:
            return 0
        for i, q in enumerate((0.25, 0.5, 0.75), start=1):
            if v <= nonzero[min(len(nonzero) - 1, int(q * len(nonzero)))]:
                return i
        return 4

    weeks = 53
    width = LEFT + weeks * STEP + PAD
    height = TOP + 7 * STEP + 44
    total = sum(values)
    active = len(nonzero)
    c = theme
    font = (
        "font-family=\"-apple-system,BlinkMacSystemFont,'Segoe UI',"
        "'Noto Sans',Helvetica,Arial,sans-serif\""
    )

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" {font}>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
        f'rx="6" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<text x="{PAD}" y="24" font-size="14" font-weight="600" '
        f'fill="{c["text"]}">{hours(total)} of coding in the last year</text>',
    ]

    # Month labels over the column where each month starts; the first
    # column is labelled only when the next month is a few weeks away.
    starts = []
    for w in range(weeks):
        for i in range(7):
            day = first + dt.timedelta(weeks=w, days=i)
            if day.day == 1:
                starts.append((w, day))
    if not starts or starts[0][0] >= 3:
        starts.insert(0, (0, first))
    for w, day in starts:
        out.append(
            f'<text x="{LEFT + w * STEP}" y="{TOP - 8}" font-size="12" '
            f'fill="{c["text"]}">{day.strftime("%b")}</text>'
        )

    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(
            f'<text x="{PAD - 2}" y="{TOP + row * STEP + 9}" font-size="12" '
            f'fill="{c["text"]}">{name}</text>'
        )

    for i, d in enumerate(span):
        v = values[i]
        x = LEFT + (i // 7) * STEP
        y = TOP + (i % 7) * STEP
        out.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{c["levels"][level(v)]}"><title>'
            f'{hours(v) if v else "No coding"} on {d.strftime("%b %-d, %Y")}'
            "</title></rect>"
        )

    base = TOP + 7 * STEP + 22
    out.append(
        f'<text x="{LEFT}" y="{base + 9}" font-size="12" fill="{c["muted"]}">'
        f"{active} active days · tracked by WakaTime</text>"
    )
    legend_x = LEFT + weeks * STEP - 5 * STEP - 34
    out.append(
        f'<text x="{legend_x - 6}" y="{base + 9}" font-size="12" '
        f'text-anchor="end" fill="{c["muted"]}">Less</text>'
    )
    for i, color in enumerate(c["levels"]):
        out.append(
            f'<rect x="{legend_x + i * STEP}" y="{base}" width="{CELL}" '
            f'height="{CELL}" rx="2" fill="{color}"/>'
        )
    out.append(
        f'<text x="{legend_x + 5 * STEP + 3}" y="{base + 9}" font-size="12" '
        f'fill="{c["muted"]}">More</text>'
    )
    out.append("</svg>")
    return "\n".join(out)


def main():
    days = json.loads(DAYS_FILE.read_text()) if DAYS_FILE.exists() else {}
    key = os.environ.get("WAKATIME_API_KEY", "").strip()
    if key:
        days.update(fetch(key))
    DAYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    DAYS_FILE.write_text(json.dumps(dict(sorted(days.items())), indent=1) + "\n")
    for name, theme in THEMES.items():
        (DAYS_FILE.parent / name).write_text(render(days, theme))
    print(f"{len(days)} days on record")


if __name__ == "__main__":
    main()
