"""Draw assets/stats.svg from live GitHub data, private repos included. Needs GH_TOKEN (a PAT of the profile owner)."""

import json
import math
import os
import urllib.request

from art import DRAW_ONCE, EASE, C, M, W, advances, col_x, head, span, svg, write

QUERY = """query{viewer{createdAt
  repositories(ownerAffiliations:OWNER,isFork:false,first:100){totalCount
    nodes{languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
  contributionsCollection{totalCommitContributions restrictedContributionsCount}}}"""

SHADES = [C["ink"], C["orange"], C["orange_tint"], C["ink60"], C["paper3"], C["paper2"]]  # five steps, then Other


def fetch(token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(f"GitHub API error: {body['errors']}")
    return body["data"]["viewer"]


def languages(repos: list[dict], top: int = 5) -> list[tuple[str, float]]:
    """Byte share per language across repos; the tail is folded into 'Other'."""
    totals: dict[str, int] = {}
    for repo in repos:
        for e in repo["languages"]["edges"]:
            totals[e["node"]["name"]] = totals.get(e["node"]["name"], 0) + e["size"]
    grand = sum(totals.values())
    if not grand:
        return []
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    out = [(name, 100 * size / grand) for name, size in ranked[:top]]
    rest = sum(size for _, size in ranked[top:])
    if rest:
        out.append(("Other", 100 * rest / grand))
    return out


def odometer(num: str, x: float, y: float, fill: str, delay: float, cid: str) -> str:
    """Each digit is a 0-9 column behind a mask that rolls to its value, like a GSAP number counter."""
    size, step = 96, 112
    xs = advances(num, size, 700, -4)
    cols = []
    for k, d in enumerate(num):
        digits = "".join(f'<text x="{x + xs[k]:.1f}" y="{y + j * step}">{j}</text>' for j in range(10))
        cols.append(
            f'<g class="roll" style="transform:translateY({-int(d) * step}px);animation-delay:{delay + 0.08 * k:.2f}s">'
            f"{digits}</g>"
        )
    return (
        f'<clipPath id="{cid}"><rect x="{x - 8}" y="{y - 84}" width="{xs[-1] + 24:.0f}" height="104"/></clipPath>'
        f'<g clip-path="url(#{cid})" font-size="{size}" font-weight="700" letter-spacing="-4" fill="{fill}">'
        + "".join(cols)
        + "</g>"
    )


def render(v: dict) -> str:
    ink, mute = C["ink"], C["ink60"]
    langs = languages(v["repositories"]["nodes"])
    cc = v["contributionsCollection"]
    commits = cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    facts = [
        (str(v["repositories"]["totalCount"]), "Repositories"),
        (str(commits), "Commits, last 12 months"),
        (v["createdAt"][:4], "On GitHub since"),
    ]
    numbers = "".join(
        f'<line class="draw" style="animation-delay:{0.1 * i:.1f}s" x1="{col_x(4 * i)}" x2="{col_x(4 * i) + span(4)}" '
        f'y1="118" y2="118" pathLength="1" stroke="{ink}"/>'
        f'<text x="{col_x(4 * i)}" y="144" font-size="16" fill="{mute}">{label}</text>'
        + odometer(num, col_x(4 * i) - 4, 236, C["orange_lg"] if i == 0 else ink, 0.2 + 0.15 * i, f"o{i}")
        for i, (num, label) in enumerate(facts)
    )
    bw, by, x = W - 2 * M, 352, float(M)
    bar = [f'<rect x="{M}" y="{by}" width="{bw}" height="10" fill="{C["paper2"]}"/>']
    legend = []
    for i, (name, pct) in enumerate(langs):
        seg = bw * pct / 100
        bar.append(
            f'<rect class="grow" style="animation-delay:{0.4 + 0.12 * i:.2f}s" x="{x:.1f}" y="{by}" '
            f'width="{max(seg - 3, 2):.1f}" height="10" fill="{SHADES[i]}"/>'
        )
        x += seg
        lx, ly = col_x(3 * (i % 4)), by + 52 + 34 * (i // 4)
        legend.append(
            f'<rect x="{lx}" y="{ly - 11}" width="12" height="12" fill="{SHADES[i]}"/>'
            f'<text x="{lx + 22}" y="{ly}" font-size="17" font-weight="600" fill="{ink}">{name}'
            f'<tspan font-weight="400" fill="{mute}">  {pct:.1f}%</tspan></text>'
        )
    h = by + 52 + 34 * ((len(langs) - 1) // 4) + 44  # last legend baseline plus the shared margin

    # Oscilloscope trace: one wavelength scrolls by per loop, so the motion has no seam.
    wl, wy = 120, 292
    pts = " ".join(
        f"{x:.0f},{wy + 9 * math.sin(2 * math.pi * x / wl) + 4 * math.sin(6 * math.pi * x / wl):.1f}"
        for x in range(M, W - M + wl + 1, 4)
    )
    wave = (
        f'<clipPath id="wv"><rect x="{M}" y="{wy - 20}" width="{bw}" height="40"/></clipPath>'
        f'<line class="draw" x1="{M}" x2="{W - M}" y1="{wy}" y2="{wy}" pathLength="1" stroke="{C["paper3"]}"/>'
        f'<g clip-path="url(#wv)"><polyline class="wave" points="{pts}" fill="none" stroke="{C["orange"]}" '
        f'stroke-width="1.6" stroke-linejoin="round"/></g>'
    )
    css = (
        DRAW_ONCE
        + f".wave{{animation:wave 3s linear infinite}}@keyframes wave{{to{{transform:translateX(-{wl}px)}}}}"
        + f".grow{{transform-box:fill-box;transform-origin:left;animation:grow 1s {EASE} both}}"
        + "@keyframes grow{from{transform:scaleX(0)}}"
        + f".roll{{animation:roll 1.6s {EASE} both}}@keyframes roll{{from{{transform:translateY(0)}}}}"
    )
    body = (
        head("In numbers", "Public and private repositories, refreshed daily")
        + numbers
        + wave
        + f'<text x="{M}" y="{by - 14}" font-size="16" fill="{mute}">Languages, by bytes of code</text>'
        + "".join(bar)
        + "".join(legend)
    )
    summary = ", ".join(f"{n} {p:.0f}%" for n, p in langs)
    return svg(
        W,
        h,
        f"In numbers: {facts[0][0]} repositories, {commits} commits in the last 12 months. Languages: {summary}.",
        css,
        body,
    )


if __name__ == "__main__":
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Set GH_TOKEN to a personal access token that can read your repositories.")
    write("stats.svg", render(fetch(token)))
