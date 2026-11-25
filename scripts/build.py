"""Generate hero.svg, why.svg and index.svg. Run: python scripts/build.py (needs requirements.txt)."""

import math

from art import BACK_OUT, DRAW_ONCE, EASE, POWER_IN_OUT, C, M, W, advances, col_x, head, kf, span, svg, write
from figures import FIGURES

NOW = [
    ("AI agentic ecosystem", "Current focus"),
    ("GE Vernova", "Software Engineering Specialist"),
    ("Design27", "Repository on GitHub"),
    ("Project Sigma and Silicon", "In development, not yet published"),
]
TOOLS = [
    ("LangGraph", "stateful agent graphs"),
    ("CrewAI", "multi-agent crews"),
    ("AutoGen", "agent conversations"),
    ("Claude Agent SDK", "agent harness"),
    ("OpenAI Agents SDK", "handoffs, guardrails"),
    ("Pydantic AI", "typed agents"),
    ("DSPy", "programmed prompts"),
    ("FastMCP", "MCP tool servers"),
]
WHY = [
    ("Why build it this way?", "Because it works."),
    ("Why does it work?", "Because every part does one job."),
    ("Why does that matter?", "Because simple parts can be reasoned about."),
    ("Why reason about it?", "So I know it is right, not hope it is."),
]

# SplitText-style entrance: each glyph rises out of a mask on its own, staggered.
SPLIT = f".ch{{animation:up 1.15s {EASE} both}}@keyframes up{{from{{transform:translateY(160px)}}}}"


def split(
    text: str,
    x: float,
    y: float,
    size: int,
    weight: int,
    track: float,
    delay: float,
    colors: dict[int, str] | None = None,
) -> str:
    xs = advances(text, size, weight, track)
    out = []
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        fill = (colors or {}).get(i, C["ink"])
        out.append(
            f'<text class="ch" style="animation-delay:{delay + 0.032 * i:.3f}s" x="{x + xs[i]:.1f}" y="{y}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">{ch}</text>'
        )
    return "".join(out)


def loop_draw(name: str, T: float, a: float, b: float) -> str:
    """DrawSVG-style stroke that draws from a to b seconds inside a T-second loop."""
    stops = [
        (0, "stroke-dashoffset:1"),
        (a, f"stroke-dashoffset:1;animation-timing-function:{POWER_IN_OUT}"),
        (b, "stroke-dashoffset:0"),
        (T, "stroke-dashoffset:0"),
    ]
    return kf(f"k{name}", T, stops) + f".{name}{{stroke-dasharray:1;animation:k{name} {T}s infinite}}"


def loop_in(
    name: str, T: float, a: float, b: float, frm: str, to: str = "opacity:1;transform:none", ease: str = EASE
) -> str:
    """One element entering between a and b seconds of a T-second loop, then holding."""
    stops = [(0, frm), (a, f"{frm};animation-timing-function:{ease}"), (b, to), (T, to)]
    return kf(f"k{name}", T, stops) + f".{name}{{animation:k{name} {T}s infinite}}"


class Seq:
    """Hands out animation classes for one loop; identical timings share a single @keyframes rule."""

    def __init__(self, T: float) -> None:
        self.T, self.css, self.names = T, [], {}

    def _cls(self, key: tuple, stops: list[tuple[float, str]], extra: str = "") -> str:
        if key not in self.names:
            n = f"s{len(self.names)}"
            self.names[key] = n
            self.css.append(kf(n, self.T, stops) + f".{n}{{animation:{n} {self.T}s infinite;{extra}}}")
        return self.names[key]

    def draw(self, a: float, b: float, e0: float, e1: float) -> str:
        """Pen in from a to b, pen out (same direction) from e0 to e1."""
        a, b, e0, e1 = (round(v, 2) for v in (a, b, e0, e1))
        stops = [
            (0, "stroke-dashoffset:1"),
            (a, f"stroke-dashoffset:1;animation-timing-function:{POWER_IN_OUT}"),
            (b, "stroke-dashoffset:0"),
            (e0, f"stroke-dashoffset:0;animation-timing-function:{POWER_IN_OUT}"),
            (e1, "stroke-dashoffset:-1"),
            (self.T, "stroke-dashoffset:-1"),
        ]
        return self._cls(("d", a, b, e0, e1), stops, "stroke-dasharray:1")

    def fade(
        self, a: float, b: float, e0: float, e1: float, frm: str, to: str, ease: str = EASE, extra: str = ""
    ) -> str:
        a, b, e0, e1 = (round(v, 2) for v in (a, b, e0, e1))
        stops = [
            (0, frm),
            (a, f"{frm};animation-timing-function:{ease}"),
            (b, to),
            (e0, f"{to};animation-timing-function:{POWER_IN_OUT}"),
            (e1, frm),
            (self.T, frm),
        ]
        return self._cls(("f", a, b, e0, e1, frm, to, ease), stops, extra)


def hero() -> str:
    h, slot = 684, 6.0  # 48 px under the descender of the g in Kandlagunta
    seq = Seq(slot * len(FIGURES))
    ink, mute = C["ink"], C["ink60"]
    right = col_x(6)

    figures, captions, progress = [], [], []
    seg = (W - M - right - 9 * 6) / len(FIGURES)
    for k, (title, line_, draw) in enumerate(FIGURES):
        base, items = k * slot, draw()
        e0, e1 = base + 5.0, base + 5.6
        parts = []
        for i, (kind, markup) in enumerate(items):
            a = base + 0.3 + 2.4 * i / len(items)
            if kind == "stroke":
                c = seq.draw(a, a + 0.8, e0, e1)
            elif kind == "pop":
                c = seq.fade(
                    a,
                    a + 0.6,
                    e0,
                    e1,
                    "transform:scale(0)",
                    "transform:scale(1)",
                    BACK_OUT,
                    "transform-box:fill-box;transform-origin:center",
                )
            else:
                c = seq.fade(a, a + 0.6, e0, e1, "opacity:0", "opacity:1")
            parts.append(markup.replace("{c}", f'class="{c}"'))
        later = ' class="later"' if k else ""
        # 90% of the drawn size, scaled about the figure box centre so the layout stays put.
        figures.append(
            f'<g id="fig{k}"{later} transform="translate(720 280) scale(.9) translate(-720 -280)">{"".join(parts)}</g>'
        )
        cap = seq.fade(
            base + 0.15, base + 0.8, e0, e1, "opacity:0;transform:translateY(10px)", "opacity:1;transform:none"
        )
        assert advances(line_, 16, 400)[-1] < W - M - right, f"caption too wide: {line_}"
        captions.append(
            f'<g{later}><g class="{cap}">'
            f'<text x="{right}" y="122" font-size="16" font-weight="600" fill="{ink}">'
            f"{title}</text>"
            f'<text x="{right}" y="144" font-size="16" fill="{mute}">{line_}</text></g></g>'
        )
        x = right + k * (seg + 6)
        on = seq.fade(base + 0.1, base + 0.5, base + 5.6, base + 5.95, "opacity:0", "opacity:1")
        progress.append(
            f'<rect x="{x:.1f}" y="160" width="{seg:.1f}" height="3" fill="{C["paper3"]}"/>'
            f'<rect class="{on}" x="{x:.1f}" y="160" width="{seg:.1f}" height="3" fill="{C["orange"]}"/>'
        )

    grid = "".join(
        f'<line class="draw" style="animation-delay:{0.035 * i:.2f}s;animation-duration:1.6s" x1="{x:.1f}" x2="{x:.1f}" '
        f'y1="0" y2="{h}" pathLength="1" stroke="{C["paper2"]}"/>'
        for i, x in enumerate([col_x(k) for k in range(12)] + [W - M])
    )
    statement = "".join(
        f'<text class="rise" style="animation-delay:{0.5 + 0.09 * i:.2f}s" x="{M}" y="{226 + 38 * i}" font-size="31" '
        f'font-weight="500" letter-spacing="-0.6" fill="{ink}">{s}</text>'
        for i, s in enumerate(["I ask why until there is", "nothing left to ask. Then", "I build up from there."])
    )
    last = "Kandlagunta."
    name = (
        f'<clipPath id="c1"><rect x="0" y="360" width="{W}" height="142"/></clipPath>'
        f'<clipPath id="c2"><rect x="0" y="502" width="{W}" height="{h - 502}"/></clipPath>'
        f'<g clip-path="url(#c1)">{split("Subramanyam", M - 6, 488, 134, 700, -6, 0.15)}</g>'
        f'<g clip-path="url(#c2)">{split(last, M - 6, 608, 134, 700, -6, 0.35, {len(last) - 1: C["orange"]})}</g>'
    )
    meta = "".join(
        f'<text class="rise" style="animation-delay:{0.3 + 0.06 * i:.2f}s" x="{M}" y="{y}" font-size="16" '
        f'font-weight="{wt}" fill="{fill}">{s}</text>'
        for i, (y, wt, fill, s) in enumerate(
            [(122, 600, ink, "Software Engineering Specialist"), (144, 400, mute, "GE Vernova, Hyderabad")]
        )
    )
    css = DRAW_ONCE + SPLIT + "".join(seq.css) + "@media (prefers-reduced-motion:reduce){.later{display:none}}"
    body = (
        grid
        + head("Profile", "2026")
        + meta
        + "".join(captions)
        + "".join(progress)
        + "".join(figures)
        + statement
        + name
    )
    title = (
        "Subramanyam Kandlagunta, Software Engineering Specialist at GE Vernova. Ten line figures draw themselves in turn: "
        + "; ".join(t for t, _, _ in FIGURES)
        + "."
    )
    return svg(W, h, title, css, body)


def why() -> str:
    T = 16.0
    x0 = col_x(5)
    top, row = 118, 88
    end_y = top + row * len(WHY)
    h = end_y + 64 + 48  # last baseline plus the same 48 px margin every section uses
    ink, mute = C["ink"], C["ink60"]
    css = [DRAW_ONCE, SPLIT]
    rows = []
    starts = [0.8 + 2.4 * i for i in range(len(WHY))]
    for i, ((q, a), s) in enumerate(zip(WHY, starts)):
        y = top + i * row
        css.append(loop_draw(f"r{i}", T, s, s + 0.8))
        css.append(loop_in(f"q{i}", T, s + 0.25, s + 1.1, "opacity:0;transform:translateY(18px)"))
        css.append(loop_in(f"a{i}", T, s + 0.8, s + 1.6, "opacity:0;transform:translateY(10px)"))
        rows.append(
            f'<line class="r{i}" x1="{x0}" x2="{W - M}" y1="{y}" y2="{y}" pathLength="1" stroke="{ink}"/>'
            f'<text class="q{i}" x="{x0}" y="{y + 32}" font-size="16" font-weight="600" fill="{C["orange_dk"]}">{i + 1}</text>'
            f'<text class="q{i}" x="{x0 + 40}" y="{y + 34}" font-size="25" font-weight="600" letter-spacing="-0.4" '
            f'fill="{ink}">{q}</text>'
            f'<text class="a{i}" x="{x0 + 40}" y="{y + 66}" font-size="21" fill="{mute}">{a}</text>'
        )
    # The depth line steps down one row per question: how far down the chain we are.
    depth = [(0, "stroke-dashoffset:1")]
    for i, s in enumerate(starts):
        depth += [
            (s, f"stroke-dashoffset:{1 - i / len(WHY):.3f};animation-timing-function:{BACK_OUT}"),
            (s + 0.7, f"stroke-dashoffset:{1 - (i + 1) / len(WHY):.3f}"),
        ]
    depth.append((T, "stroke-dashoffset:0"))
    css.append(kf("dep", T, depth) + f".dep{{stroke-dasharray:1;animation:dep {T}s infinite}}")

    fs = starts[-1] + 2.6
    final = "Understand it, then build it."
    fx = advances(final, 36, 700, -1)
    words, start = [], 0
    for wi, word in enumerate(final.split(" ")):
        words.append(
            f'<text class="w{wi}" x="{x0 + fx[start]:.1f}" y="{end_y + 64}" font-size="36" font-weight="700" '
            f'letter-spacing="-1" fill="{ink}">{word}</text>'
        )
        css.append(
            loop_in(f"w{wi}", T, fs + 0.35 + 0.09 * wi, fs + 1.1 + 0.09 * wi, "opacity:0;transform:translateY(26px)")
        )
        start += len(word) + 1
    css.append(loop_draw("fr", T, fs, fs + 0.9))

    # Recursion drawn: each question turns one square deeper; the last one fills at the first principle.
    vx, vy, side = M + 75, top + 268, 150  # flush with the left margin
    vortex = []
    for k in range(len(WHY) + 1):
        half, rot = side * 0.78**k / 2, math.radians(14 * k)
        pts = " ".join(
            f"{vx + half * math.sqrt(2) * math.cos(rot + math.pi / 4 + q * math.pi / 2):.1f},"
            f"{vy + half * math.sqrt(2) * math.sin(rot + math.pi / 4 + q * math.pi / 2):.1f}"
            for q in range(4)
        )
        at = starts[k] if k < len(WHY) else fs
        css.append(loop_draw(f"v{k}", T, at, at + 0.9))
        vortex.append(
            f'<polygon class="v{k}" points="{pts}" pathLength="1" fill="none" stroke="{ink}" stroke-width="1.4"/>'
        )
        if k == len(WHY):
            css.append(loop_in("vf", T, fs + 0.6, fs + 1.3, "opacity:0", "opacity:1"))
            vortex.append(f'<polygon class="vf" points="{pts}" fill="{C["orange"]}"/>')
    css.append(loop_in("chain", T, 14.6, 15.4, "opacity:1", "opacity:0", POWER_IN_OUT))

    body = (
        head("On method", "Four questions deep")
        + f'<clipPath id="cw"><rect x="0" y="{top}" width="{x0 - 30}" height="140"/></clipPath>'
        + f'<g clip-path="url(#cw)">{split("Why?", M - 4, top + 118, 128, 700, -6, 0.1, {3: C["orange_lg"]})}</g>'
        + f'<text class="rise" style="animation-delay:.5s" x="{M}" y="{top + 168}" font-size="16" fill="{mute}">'
        "Asked until nothing is left to ask.</text>"
        + '<g class="chain">'
        + f'<line class="dep" x1="{x0 - 22}" x2="{x0 - 22}" y1="{top}" y2="{end_y}" pathLength="1" '
        f'stroke="{C["orange"]}" stroke-width="4"/>'
        + "".join(rows)
        + f'<line class="fr" x1="{x0}" x2="{W - M}" y1="{end_y + 8}" y2="{end_y + 8}" pathLength="1" '
        f'stroke="{C["orange"]}" stroke-width="3"/>' + "".join(words) + "".join(vortex) + "</g>"
    )
    alt = "Why? Four questions deep. " + " ".join(f"{q} {a}" for q, a in WHY) + " " + final
    return svg(W, h, alt, "".join(css), body)


def index() -> str:
    top, row, T = 118, 68, 8.0
    h = top + row * 3 + 54 + 48  # last baseline plus the shared 48 px margin
    ink, mute = C["ink"], C["ink60"]
    css = [DRAW_ONCE]
    now = "".join(
        f'<line class="draw" style="animation-delay:{0.1 * i:.1f}s" x1="{M}" x2="{M + span(5)}" y1="{top + row * i}" '
        f'y2="{top + row * i}" pathLength="1" stroke="{ink}"/>'
        f'<text class="rise" style="animation-delay:{0.1 * i + 0.25:.2f}s" x="{M}" y="{top + row * i + 32}" '
        f'font-size="21" font-weight="600" fill="{ink}">{title}</text>'
        f'<text class="rise" style="animation-delay:{0.1 * i + 0.3:.2f}s" x="{M}" y="{top + row * i + 54}" '
        f'font-size="15" fill="{C["orange_dk"] if i == 0 else mute}">{detail}</text>'
        for i, (title, detail) in enumerate(NOW)
    )
    cols = [col_x(6), col_x(9)]
    cells, spots = [], []
    for i, (name, kind) in enumerate(TOOLS):
        x, r = cols[i // 4], i % 4
        y = top + row * r
        cells.append(
            f'<line class="draw" style="animation-delay:{0.2 + 0.06 * i:.2f}s" x1="{x}" x2="{x + span(3) - 8}" '
            f'y1="{y}" y2="{y}" pathLength="1" stroke="{ink}"/>'
            f'<text class="rise" style="animation-delay:{0.35 + 0.06 * i:.2f}s" x="{x}" y="{y + 32}" '
            f'font-size="21" font-weight="600" fill="{ink}">{name}</text>'
            f'<text class="rise" style="animation-delay:{0.4 + 0.06 * i:.2f}s" x="{x}" y="{y + 54}" '
            f'font-size="15" fill="{mute}">{kind}</text>'
        )
        spots.append((x - 20, y + 25))  # marker sits in the gutter, names get the full column
    # An orange marker hops down the tool list, one stop per second, settling with a spring.
    walk = []
    for i, (x, y) in enumerate(spots):
        at = f"transform:translate({x}px,{y - 6}px);animation-timing-function:{BACK_OUT}"
        walk += [(i, at), (i + 0.55, at)]
    walk.append((T, f"transform:translate({spots[0][0]}px,{spots[0][1] - 6}px)"))
    css.append(kf("walk", T, walk) + f".mk{{animation:walk {T}s infinite}}")

    # A two-line circuit trace in the gutter between the columns; signal pulses run down it.
    gx = (M + span(5) + cols[0]) / 2
    traces, pads = [], []
    for j, dx in enumerate((-8, 8)):
        x = gx + dx
        d = f"M{x} {top}V{top + 58}L{x + 20} {top + 78}V{top + 146}L{x} {top + 166}V{top + 226}L{x + 20} {top + 246}V{h - 48}"
        traces.append(
            f'<path class="draw" style="animation-delay:{0.3 + 0.15 * j:.2f}s" d="{d}" pathLength="1" fill="none" '
            f'stroke="{ink}" stroke-width="1.4" stroke-linejoin="round"/>'
            f'<path class="pulse" style="animation-delay:{-1.4 * j:.1f}s" d="{d}" pathLength="1" fill="none" '
            f'stroke="{C["orange"]}" stroke-width="3" stroke-linecap="round"/>'
        )
        pads += [(x, top), (x + 20, h - 48)]
    css.append(".pulse{stroke-dasharray:.07 1;animation:pulse 2.8s linear infinite}")
    css.append("@keyframes pulse{from{stroke-dashoffset:.07}to{stroke-dashoffset:-1}}")
    trace = "".join(traces) + "".join(
        f'<circle class="rise" style="animation-delay:.9s" cx="{x}" cy="{y}" r="4" fill="{C["paper"]}" stroke="{ink}" stroke-width="1.4"/>'
        for x, y in pads
    )
    body = (
        f'<line class="draw" x1="{M}" x2="{M + span(5)}" y1="48" y2="48" pathLength="1" stroke="{ink}" stroke-width="3"/>'
        f'<text x="{M}" y="78" font-size="16" font-weight="600" fill="{ink}">Currently</text>'
        f'<line class="draw" x1="{cols[0]}" x2="{W - M}" y1="48" y2="48" pathLength="1" stroke="{ink}" stroke-width="3"/>'
        f'<text x="{cols[0]}" y="78" font-size="16" font-weight="600" fill="{ink}">Tools</text>'
        + now
        + trace
        + "".join(cells)
        + f'<rect class="mk" width="12" height="12" fill="{C["orange"]}" '
        f'transform="translate({spots[0][0]} {spots[0][1] - 6})"/>'
    )
    alt = "Currently: " + "; ".join(f"{t}, {d}" for t, d in NOW) + ". Tools: " + ", ".join(n for n, _ in TOOLS) + "."
    return svg(W, h, alt, "".join(css), body)


if __name__ == "__main__":
    write("hero.svg", hero())
    write("why.svg", why())
    write("index.svg", index())
