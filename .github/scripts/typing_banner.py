"""Writes assets/typing.svg: the intro lines typed out and erased in turn,
with the ChowTap logo appearing after the last line.

Plain SMIL animation (no scripts or external fonts), so it plays when
GitHub shows it as an image. Run it again after changing LINES.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "typing.svg"

# (text, show the ChowTap logo after it)
LINES = [
    ("Hey, I'm Ini 👋", False),
    ("I build mobile apps people actually use", False),
    ("Flutter / Dart • Swift • Node", False),
    ("Currently shipping ChowTap", True),
]

W, H = 640, 50
SIZE = 22
CHAR = SIZE * 0.6  # monospace advance
COLOR = "#A78BFA"
TYPE, ERASE, HOLD, GAP = 0.07, 0.025, 1.6, 0.35  # seconds
LOGO = 30  # logo height in px
LOGO_GAP = 10

# ChowTap mark (assets/svg/chowtap logo new.svg in chowtap_mobile).
LOGO_SVG = """<svg viewBox="0 0 106 100" width="{w}" height="{h}" x="{x}" y="{y}">
<path d="M22.5197 9.89015C22.5197 9.89015 45.2497 -6.92985 71.3797 3.30015C97.5097 13.5301 102.75 35.8001 102.75 35.8001C102.75 35.8001 114.11 61.7001 90.2497 80.8001C66.3897 99.9001 32.5197 103.53 18.2497 95.1201C3.97968 86.7101 -2.90032 65.2301 1.15968 42.1601C4.91968 20.8001 22.5197 9.89015 22.5197 9.89015Z" fill="white"/>
<path d="M31.6 48.8399C31.5109 42.5481 32.8083 36.3138 35.4 30.5799C38.1018 24.9355 42.3318 20.1615 47.61 16.7999C49.4239 15.5063 51.4232 14.4949 53.54 13.7999C55.6109 13.1351 57.7518 12.7123 59.92 12.5399C61.7422 12.3714 63.5776 12.6601 65.26 13.3799C66.7095 14.0155 67.9902 14.9812 69 16.1999C70.0105 17.4393 70.765 18.8669 71.22 20.3999C71.716 21.9559 71.9789 23.5769 72 25.2099C72.0025 26.2426 71.9122 27.2734 71.73 28.2899V28.1999C71.61 28.6999 71.47 29.1999 71.32 29.6499C71.17 30.0999 71.01 30.6499 70.82 31.0999C70.4034 32.2512 69.6639 33.258 68.69 33.9999C67.832 34.6632 66.7744 35.0158 65.69 34.9999C64.9632 34.9989 64.2423 34.8702 63.56 34.6199C62.8723 34.379 62.2423 33.9976 61.71 33.4999L61.35 33.1299H61.44C59.6267 30.6433 57.8767 29.3966 56.19 29.3899C55.0386 29.4613 53.9612 29.982 53.19 30.8399C52.1238 31.8986 51.2237 33.1123 50.52 34.4399C49.4344 36.1713 48.5105 37.9991 47.76 39.8999C47.0036 41.8094 46.62 43.8461 46.63 45.8999C46.6293 46.6618 46.6727 47.4231 46.76 48.1799C46.8505 48.9579 47.018 49.725 47.26 50.4699C47.7827 52.1177 48.7273 53.6001 50 54.7699C51.039 55.7943 52.4312 56.3813 53.89 56.4099C55.7472 56.3374 57.5347 55.6832 59 54.5399L60.27 53.6099C60.81 53.1699 61.36 52.7499 61.9 52.3399C62.4652 51.9223 63.0717 51.5638 63.71 51.2699C65.0036 50.4066 66.4989 49.8933 68.05 49.7799C70.2767 49.7799 71.9067 51.5233 72.94 55.0099C73.4867 56.6226 73.79 58.3078 73.84 60.0099C73.8468 61.355 73.3834 62.6602 72.53 63.6999C71.3967 65.0217 70.1035 66.1974 68.68 67.1999C67.2165 68.1118 65.6931 68.9237 64.12 69.6299C62.46 70.3699 60.77 71.0366 59.05 71.6299C57.3543 72.214 55.6157 72.6654 53.85 72.9799C52.1783 73.284 50.4751 73.3781 48.78 73.2599C46.7261 73.1478 44.7129 72.642 42.85 71.7699C41.0246 70.9007 39.3581 69.7311 37.92 68.3099C36.4309 66.8239 35.1946 65.1046 34.26 63.2199C33.2483 61.1784 32.5729 58.9868 32.26 56.7299C32.14 55.4199 32.04 54.1099 31.95 52.7999C31.86 51.4899 31.72 50.1499 31.6 48.8399Z" fill="#CB2127"/>
<path d="M34.8502 90.1403C39.6495 90.1403 43.5402 86.2496 43.5402 81.4502C43.5402 76.6509 39.6495 72.7603 34.8502 72.7603C30.0508 72.7603 26.1602 76.6509 26.1602 81.4502C26.1602 86.2496 30.0508 90.1403 34.8502 90.1403Z" fill="#CB2127"/>
</svg>"""


def width_of(text):
    # Emoji take about two monospace cells.
    return sum(2 if ord(ch) > 0x2FFF else 1 for ch in text) * CHAR


def main():
    # Each line: (start x, [(time, revealed width)]), on one shared clock.
    t = 0.0
    plans = []
    for text, logo in LINES:
        text_w = width_of(text)
        full = text_w + (LOGO_GAP + LOGO * 1.06 if logo else 0)
        x0 = (W - full) / 2
        steps = [(t, 0.0)]
        for i in range(1, len(text) + 1):
            t += TYPE
            steps.append((t, width_of(text[:i])))
        if logo:
            t += TYPE * 3
            steps.append((t, full))
        t += HOLD
        if logo:
            steps.append((t, text_w))
            t += ERASE * 3
        for i in range(len(text) - 1, -1, -1):
            steps.append((t, width_of(text[:i])))
            t += ERASE
        steps.append((t, 0.0))
        t += GAP
        plans.append((x0, text_w, full, logo, text, steps))
    total = t

    def anim(attr, pairs, extra=""):
        times, values = [], []
        for when, value in pairs:
            key = round(when / total, 5)
            if times and key <= times[-1]:
                key = round(times[-1] + 0.00001, 5)
            times.append(key)
            values.append(value)
        if times[0] != 0:
            times.insert(0, 0)
            values.insert(0, values[0])
        return (
            f'<animate attributeName="{attr}" dur="{total:.2f}s" '
            f'repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="{";".join(map(str, times))}" '
            f'values="{";".join(values)}"{extra}/>'
        )

    font = ("'Fira Code','JetBrains Mono',SFMono-Regular,Menlo,"
            "Consolas,'Liberation Mono',monospace")
    base = H / 2 + SIZE * 0.36
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">',
        "<defs>",
    ]
    for i, (x0, _, _, _, _, steps) in enumerate(plans):
        out.append(f'<clipPath id="c{i}"><rect x="{x0:.1f}" y="0" '
                   f'height="{H}" width="0">')
        out.append(anim("width", [(s, f"{w:.1f}") for s, w in steps]))
        out.append("</rect></clipPath>")
    out.append("</defs>")

    cursor = []
    for i, (x0, text_w, full, logo, text, steps) in enumerate(plans):
        out.append(f'<g clip-path="url(#c{i})">')
        out.append(
            f'<text x="{x0:.1f}" y="{base:.1f}" font-family="{font}" '
            f'font-size="{SIZE}" font-weight="600" fill="{COLOR}" '
            f'textLength="{text_w:.1f}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve">{text}</text>'
        )
        if logo:
            out.append(LOGO_SVG.format(
                w=LOGO * 1.06, h=LOGO, x=f"{x0 + text_w + LOGO_GAP:.1f}",
                y=f"{(H - LOGO) / 2:.1f}",
            ))
        out.append("</g>")
        cursor += [(s, f"{x0 + w + 2:.1f}") for s, w in steps]

    out.append(
        f'<rect y="{(H - SIZE * 1.15) / 2:.1f}" width="2.5" '
        f'height="{SIZE * 1.15:.1f}" fill="{COLOR}">'
    )
    out.append(anim("x", cursor))
    out.append('<animate attributeName="opacity" values="1;1;0;0" '
               'keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/>')
    out.append("</rect>")
    out.append("</svg>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out) + "\n")
    print(f"{OUT.relative_to(ROOT)}: {total:.1f}s loop")


if __name__ == "__main__":
    main()
