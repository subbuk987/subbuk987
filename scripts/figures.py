"""The ten hero figures. Each is a caption plus ordered primitives that the sequencer animates.

Primitive kinds: "stroke" draws like a pen, "pop" springs in, "fill" and "label" fade in.
Every markup string holds {c} where the sequencer puts the animation class.
All figures live in the box x 528-912, y 172-390, centred on (720, 280).
"""

import math

from art import C

INK, MUTE, OR = C["ink"], C["ink60"], C["orange"]
X, Y = 720, 280
Item = tuple[str, str]


def line(x1: float, y1: float, x2: float, y2: float, w: float = 2) -> Item:
    return (
        "stroke",
        f'<line {{c}} x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" pathLength="1" stroke="{INK}" stroke-width="{w}"/>',
    )


def path(d: str, w: float = 2, color: str = INK) -> Item:
    return (
        "stroke",
        f'<path {{c}} d="{d}" pathLength="1" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"/>',
    )


def ring(x: float, y: float, r: float, w: float = 1.4) -> Item:
    return (
        "stroke",
        f'<circle {{c}} cx="{x:.1f}" cy="{y:.1f}" r="{r}" pathLength="1" fill="none" stroke="{INK}" stroke-width="{w}"/>',
    )


def dot(x: float, y: float, r: float = 5, color: str = INK) -> Item:
    return ("pop", f'<circle {{c}} cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"/>')


def fill(markup: str) -> Item:
    return ("fill", markup)


def label(x: float, y: float, s: str, anchor: str = "start", size: int = 15) -> Item:
    return (
        "label",
        f'<text {{c}} x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="500" text-anchor="{anchor}" fill="{MUTE}">{s}</text>',
    )


def arc_arrow(r: float, a0: float, a1: float) -> list[Item]:
    """Clockwise arc around (X, Y) from a0 to a1 degrees, with a chevron head at the end."""
    p = lambda a, rr=r: (X + rr * math.cos(math.radians(a)), Y + rr * math.sin(math.radians(a)))  # noqa: E731
    (x0, y0), (x1, y1) = p(a0), p(a1)
    tx, ty = -math.sin(math.radians(a1)), math.cos(math.radians(a1))  # clockwise tangent
    nx, ny = math.cos(math.radians(a1)), math.sin(math.radians(a1))
    h = 9
    left = (x1 - tx * h + nx * h * 0.6, y1 - ty * h + ny * h * 0.6)
    right = (x1 - tx * h - nx * h * 0.6, y1 - ty * h - ny * h * 0.6)
    return [
        path(f"M{x0:.1f} {y0:.1f}A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}", 1.6),
        path(f"M{left[0]:.1f} {left[1]:.1f}L{x1:.1f} {y1:.1f}L{right[0]:.1f} {right[1]:.1f}", 1.6),
    ]


def euclid() -> list[Item]:
    L = 112
    ax, bx, cy = X - L / 2, X + L / 2, Y
    c = cy - L * math.sqrt(3) / 2
    return [
        line(ax, cy, bx, cy, 2.5),
        dot(ax, cy),
        label(ax - 22, cy + 26, "A"),
        dot(bx, cy),
        label(bx + 12, cy + 26, "B"),
        ring(ax, cy, L, 1.2),
        ring(bx, cy, L, 1.2),
        dot(X, c),
        label(X + 14, c + 4, "C"),
        line(ax, cy, X, c, 2.5),
        line(bx, cy, X, c, 2.5),
        fill(f'<polygon {{c}} points="{ax},{cy} {bx},{cy} {X},{c:.1f}" fill="{OR}"/>'),
    ]


def transistor() -> list[Item]:
    return [
        line(600, 280, 676, 280),
        line(676, 222, 676, 338, 3),
        line(696, 214, 696, 246, 3),
        line(696, 264, 696, 296, 3),
        line(696, 314, 696, 346, 3),
        path("M696 230H784V176"),
        path("M696 330H784V384"),
        path("M696 280H784V330"),
        fill(f'<polygon {{c}} points="700,280 718,271 718,289" fill="{INK}"/>'),
        dot(600, 280, 6, OR),
        label(588, 270, "gate", "end"),
        label(798, 190, "drain"),
        label(798, 380, "source"),
    ]


def nand() -> list[Item]:
    return [
        line(590, 250, 650, 250),
        line(590, 310, 650, 310),
        path("M650 214H700A66 66 0 0 1 700 346H650Z", 2.5),
        ring(776, 280, 9, 2.5),
        line(785, 280, 860, 280),
        label(578, 255, "A", "end"),
        label(578, 315, "B", "end"),
        label(872, 285, "Y"),
        fill(f'<circle {{c}} cx="776" cy="280" r="7" fill="{OR}"/>'),
        label(700, 375, "Y = not (A and B)", "middle", 14),
    ]


def cpu() -> list[Item]:
    pins = [640 + 18 + 25 * i for i in range(6)]
    top = "".join(f"M{x} 200V180" for x in pins)
    bot = "".join(f"M{x} 360V380" for x in pins)
    lft = "".join(f"M640 {x - 440}H620" for x in pins)  # same spacing as the top pins, turned 90 degrees
    rgt = "".join(f"M800 {x - 440}H820" for x in pins)
    cores = "M660 220h56v56h-56zM724 220h56v56h-56zM660 284h56v56h-56zM724 284h56v56h-56z"
    return [
        path("M640 200H800V360H640Z", 2.5),
        path(top, 1.6),
        path(rgt, 1.6),
        path(bot, 1.6),
        path(lft, 1.6),
        path(cores, 1.2),
        fill(f'<rect {{c}} x="724" y="284" width="56" height="56" fill="{OR}"/>'),
        label(840, 285, "4 cores"),
    ]


def cycle() -> list[Item]:
    r, nodes = 80, [(-90, "fetch"), (30, "decode"), (150, "execute")]
    items: list[Item] = []
    for a, name in nodes:
        x, y = X + r * math.cos(math.radians(a)), Y + r * math.sin(math.radians(a))
        items += [ring(x, y, 30, 2), label(x, y + 5, name, "middle", 14)]
    for a, _ in nodes:
        items += arc_arrow(r, a + 24, a + 120 - 24)
    items.append(dot(X, Y, 7, OR))
    return items


def perceptron() -> list[Item]:
    ys = [214, 280, 346]
    items: list[Item] = []
    for i, y in enumerate(ys):
        items += [
            ring(596, y, 11, 2),
            line(607, y, 692, 280 + (y - 280) * 0.25, 1.6),
            label(640, y - 12 if y < 280 else y + 22, f"w{i + 1}", "middle", 14),
        ]
    items += [
        ring(720, 280, 28, 2.5),
        path("M730 268H711L722 280L711 292H730", 2),
        line(748, 280, 800, 280),
        path("M808 300H836V258H866", 2.5),
        fill(f'<circle {{c}} cx="720" cy="280" r="26" fill="{OR}" fill-opacity=".25"/>'),
        label(596, 380, "inputs", "middle", 14),
        label(836, 330, "threshold", "middle", 14),
    ]
    return items


def network() -> list[Item]:
    layers = [(610, 3), (683, 4), (757, 4), (830, 2)]
    pos = [[(x, Y + (j - (n - 1) / 2) * 52) for j in range(n)] for x, n in layers]
    items: list[Item] = []
    for a, b in zip(pos, pos[1:]):
        d = "".join(f"M{x1} {y1:.0f}L{x2} {y2:.0f}" for x1, y1 in a for x2, y2 in b)
        items.append(path(d, 0.9))
    for layer in pos:
        items += [dot(x, y, 8) for x, y in layer]
    hot = [pos[0][1], pos[1][1], pos[2][2], pos[3][1]]
    items.append(path("M" + "L".join(f"{x} {y:.0f}" for x, y in hot), 3, OR))
    items += [label(610, 380, "input", "middle", 14), label(830, 380, "output", "middle", 14)]
    return items


def descent() -> list[Item]:
    mx, my = 760, 290
    items: list[Item] = [
        (
            "stroke",
            f'<ellipse {{c}} cx="{mx}" cy="{my}" rx="{rx}" ry="{ry}" transform="rotate(-14 {mx} {my})" pathLength="1" fill="none" stroke="{INK}" stroke-width="1.2"/>',
        )
        for rx, ry in [(136, 74), (102, 55), (70, 37), (38, 19)]
    ]
    steps = [(612, 216), (660, 258), (694, 238), (722, 278), (742, 272), (753, 288), (760, 290)]
    items.append(path("M" + "L".join(f"{x} {y}" for x, y in steps), 2.5, OR))
    items += [dot(x, y, 4.5) for x, y in steps]
    items.append(label(612, 200, "start", "middle", 14))
    return items


def attention() -> list[Item]:
    n, s, x0, y0 = 6, 28, 636, 196
    grid = "".join(f"M{x0} {y0 + i * s}h{n * s}" for i in range(n + 1)) + "".join(
        f"M{x0 + i * s} {y0}v{n * s}" for i in range(n + 1)
    )
    items: list[Item] = [path(grid, 1)]
    for i in range(n):
        cells = "".join(
            f'<rect x="{x0 + j * s + 2}" y="{y0 + i * s + 2}" width="{s - 4}" height="{s - 4}" fill="{OR}" '
            f'fill-opacity="{0.1 + 0.9 * math.exp(-((i - j) ** 2) / 1.6) * (0.55 + 0.45 * ((i * 7 + j * 3) % 5) / 4):.2f}"/>'
            for j in range(n)
        )
        items.append(fill(f"<g {{c}}>{cells}</g>"))
    items += [
        label(x0 + n * s / 2, y0 - 12, "keys", "middle", 14),
        label(x0 - 12, y0 + n * s / 2 + 5, "queries", "end", 14),
    ]
    return items


def agent() -> list[Item]:
    r = 96
    nodes = [(-90, "observe"), (30, "act"), (150, "reason")]
    items: list[Item] = [ring(X, Y, 30, 2.5)]
    for a, _ in nodes:
        items += arc_arrow(r, a + 14, a + 120 - 14)
    for a, name in nodes:
        x, y = X + r * math.cos(math.radians(a)), Y + r * math.sin(math.radians(a))
        dx = 0 if a == -90 else (16 if a == 30 else -16)
        if a == -90:
            items += [dot(x, y, 6), label(x + 14, y + 5, name, "start", 14)]
        else:
            items += [dot(x, y, 6), label(x + dx, y + 24, name, "start" if a == 30 else "end", 14)]
    items += [
        line(X + r * math.cos(math.radians(30)) + 6, Y + r * math.sin(math.radians(30)) - 6, 848, 252, 1.6),
        path("M848 236h56v32h-56z", 2),
        label(876, 257, "tool", "middle", 14),
        fill(f'<circle {{c}} cx="{X}" cy="{Y}" r="27" fill="{OR}"/>'),
        (
            "label",
            f'<text {{c}} x="{X}" y="{Y + 5}" font-size="14" font-weight="600" text-anchor="middle" fill="{INK}">agent</text>',
        ),
    ]
    return items


FIGURES = [
    ("Euclid, Elements I.1", "On a given line, construct an equilateral triangle.", euclid),
    ("The transistor", "A switch. Every chip is billions of them.", transistor),
    ("NAND gate", "Universal: any logic can be built from it alone.", nand),
    ("The processor", "A die, its pins, and cores working in parallel.", cpu),
    ("Instruction cycle", "Fetch, decode, execute, billions of times a second.", cycle),
    ("Perceptron", "Weighted inputs, a sum, a threshold. One neuron.", perceptron),
    ("Neural network", "Layers of neurons. Depth is where learning lives.", network),
    ("Gradient descent", "Step downhill on the error until it stops falling.", descent),
    ("Attention", "Each token weighs all others. Core of transformers.", attention),
    ("Agent loop", "Observe, reason, act with tools, then observe again.", agent),
]
