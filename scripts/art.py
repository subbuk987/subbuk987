"""Swiss editorial system for the profile SVGs: palette, 12-column grid, font, keyframe helper."""

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

C = {
    "paper": "#F5E8D8",  # warm beige
    "paper2": "#EADBC8",  # grid hairlines
    "paper3": "#D9C7B0",  # rules, bar track
    "ink": "#1C1C1C",  # soft black
    "ink60": "#5C554D",  # secondary text, 6.1:1 on paper
    "orange": "#FF4500",  # burnt orange: shapes, rules, fills only (2.9:1)
    "orange_lg": "#E63E00",  # orange for large type (3.5:1)
    "orange_dk": "#B83200",  # orange for small text (5.0:1)
    "orange_tint": "#FF8F66",
}

W, M, GUT, COLS = 960, 48, 16, 12
COL = (W - 2 * M - GUT * (COLS - 1)) / COLS


def col_x(i: int) -> float:
    return M + i * (COL + GUT)


def span(cols: int) -> float:
    return cols * COL + (cols - 1) * GUT


def font_css() -> str:
    b64 = base64.b64encode((ROOT / "art/fonts/hanken.woff2").read_bytes()).decode()
    return (
        f"@font-face{{font-family:H;font-weight:100 900;src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
        "text{font-family:H,Helvetica,Arial,sans-serif;font-feature-settings:'tnum'}"
    )


REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
EASE = "cubic-bezier(.16,1,.3,1)"  # gsap expo.out


def kf(name: str, total: float, stops: list[tuple[float, str]]) -> str:
    """Keyframes from (seconds, declarations) pairs; times become percentages of the loop."""
    body = "".join(f"{100 * t / total:.2f}%{{{css}}}" for t, css in stops)
    return f"@keyframes {name}{{{body}}}"


def svg(w: int, h: int, title: str, css: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{title}"><title>{title}</title>'
        f"<style>{font_css()}{css}{REDUCED}</style>"
        f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>{body}</svg>'
    )


def head(left: str, right: str = "", y: int = 48) -> str:
    """Swiss section head: a heavy rule that draws in, then a label row under it."""
    out = (
        f'<line class="draw" x1="{M}" x2="{W - M}" y1="{y}" y2="{y}" pathLength="1" '
        f'stroke="{C["ink"]}" stroke-width="3"/>'
        f'<text x="{M}" y="{y + 30}" font-size="16" font-weight="600" fill="{C["ink"]}">{left}</text>'
    )
    if right:
        out += f'<text x="{W - M}" y="{y + 30}" font-size="16" text-anchor="end" fill="{C["ink60"]}">{right}</text>'
    return out


# Lines draw in once on load. Base state is the finished drawing, so no-animation viewers see it complete.
DRAW_ONCE = (
    f".draw{{stroke-dasharray:1;animation:draw 1.1s {EASE} both}}"
    "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
    f".rise{{animation:rise .9s {EASE} both}}"
    "@keyframes rise{from{transform:translateY(24px);opacity:0}}"
)


def write(name: str, content: str) -> None:
    path = ROOT / "assets" / name
    path.write_text(content)
    print(f"wrote {path.relative_to(ROOT)} ({len(content) // 1024} KB)")


# GSAP's easing curves, as CSS cubic-beziers.
EXPO_OUT = "cubic-bezier(.16,1,.3,1)"  # gsap expo.out
BACK_OUT = "cubic-bezier(.34,1.56,.64,1)"  # gsap back.out(1.7): a small overshoot, like a spring settling
POWER_IN_OUT = "cubic-bezier(.76,0,.24,1)"  # gsap power4.inOut

_ADV: dict[int, tuple[dict[str, int], dict[int, str], int]] = {}


def advances(text: str, size: float, weight: int, tracking: float = 0) -> list[float]:
    """Pen x-offset of every character, so each letter can animate on its own (SplitText-style)."""
    if weight not in _ADV:
        from fontTools.ttLib import TTFont  # build-time only: lets the SVGs place letters without a browser
        from fontTools.varLib.instancer import instantiateVariableFont

        font = instantiateVariableFont(TTFont(ROOT / "art/fonts/hanken.woff2"), {"wght": weight})
        _ADV[weight] = (
            {g: a for g, (a, _) in font["hmtx"].metrics.items()},
            font.getBestCmap(),
            font["head"].unitsPerEm,
        )
    widths, cmap, upm = _ADV[weight]
    xs, x = [], 0.0
    for ch in text:
        xs.append(x)
        x += widths[cmap[ord(ch)]] * size / upm + tracking
    return xs + [x]
