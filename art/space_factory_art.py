"""Theme-aware vector art for the eight compact space-factory silhouettes.

These icons deliberately remain SVG even in raster critter themes: each one is
an independent, status-free card illustration and the renderer can scale it to
the 24 px card tile without an extra raster dependency.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDINGS = (
    "mill",
    "power",
    "tank",
    "warehouse",
    "foundry",
    "waterworks",
    "assembly",
    "refinery",
)

# Palette and finish are kept here, separate from the factory geometry, so a
# silhouette keeps its identity as the selected theme changes.
STYLES = {
    "retro": {
        "outline": "#241b2e", "wall": "#9b6948", "roof": "#d27a3c",
        "shade": "#5c4568", "trim": "#f2b94d", "window": "#f5e29a",
        "line": "#38253d", "extra": "#5ed8dd", "render": 'shape-rendering="crispEdges"',
        "finish": '<path class="finish" d="M5 14h2v7H5z M17 14h2v7h-2z"/>',
    },
    "edo": {
        "outline": "#292b36", "wall": "#e4d4b4", "roof": "#385b7b",
        "shade": "#c19a70", "trim": "#c74430", "window": "#d7e0d1",
        "line": "#303447", "extra": "#b84432", "render": 'shape-rendering="geometricPrecision"',
        "finish": '<path class="finish" d="M5 15h14 M5 17h3 M16 17h3 M5 19h14"/>',
    },
    "y2k": {
        "outline": "#6e8298", "wall": "url(#wallGradient)", "roof": "url(#roofGradient)",
        "shade": "#91aeca", "trim": "#c3f56a", "window": "#f7ffff",
        "line": "#7694ad", "extra": "#ee7bd7", "render": 'shape-rendering="geometricPrecision"',
        "finish": '<path class="finish" d="M5 14h13l-2 2H6z"/>',
    },
    "noir": {
        "outline": "#25262a", "wall": "#aaa69b", "roof": "#5c5d62",
        "shade": "#3b3c41", "trim": "#d7cdb5", "window": "#e4cb91",
        "line": "#38383d", "extra": "#bb303b", "render": 'shape-rendering="crispEdges"',
        "finish": '<path class="finish" d="M5 14h14v1H5z M5 20h14v1H5z"/>',
    },
    "deepsea": {
        "outline": "#103354", "wall": "url(#gelGradient)", "roof": "#17628a",
        "shade": "#183d70", "trim": "#74ffff", "window": "#c5ffff",
        "line": "#53e4ef", "extra": "#ff8bdf", "render": 'shape-rendering="geometricPrecision"',
        "finish": '<path class="finish" d="M5 14h14 M5 20h14"/>',
    },
    "garden": {
        "outline": "#624936", "wall": "#d9aa72", "roof": "#91b775",
        "shade": "#bb806f", "trim": "#fff0c9", "window": "#f8f2d8",
        "line": "#75553d", "extra": "#e07aa5", "render": 'shape-rendering="geometricPrecision"',
        "finish": '<path class="finish" d="M5 14h14 M5 20h14"/>',
    },
    "cyber": {
        "outline": "#20143a", "wall": "#302044", "roof": "#45235d",
        "shade": "#160e29", "trim": "#00efff", "window": "#39ff90",
        "line": "#ff37d7", "extra": "#ff37d7", "render": 'shape-rendering="geometricPrecision"',
        "finish": '<path class="finish" d="M5 14h14 M5 20h14"/>',
    },
}

# Each upper structure has a distinct skyline; all share a small front wall so
# the live space-color sign can sit in one consistent spot in the UI.
UPPERS = {
    "mill": '''
      <path class="roof" d="M3 14V9l3-3v5l3-3v5l3-3v5l3-3v3h6v-1z"/>
      <path class="edge" d="M3 14V9l3-3v5l3-3v5l3-3v5l3-3v3h6"/>
      <path class="trimline" d="M6 9v2m3-2v2m3-2v2m3-2v2"/>
    ''',
    "power": '''
      <path class="roof" d="M4 11h16v3H4z"/>
      <path class="edge" d="M4 11h16v3H4z"/>
      <path class="shade" d="M6 4h3v8H6zM15 2h3v10h-3z"/>
      <path class="edge" d="M6 4h3v8H6zM15 2h3v10h-3z"/>
      <path class="trimline" d="M5 4h5M14 2h5"/>
    ''',
    "tank": '''
      <path class="roof" d="M4 12h16v2H4z"/>
      <path class="shade" d="M5 8a3 2 0 0 1 6 0v5H5zM13 6a3 2 0 0 1 6 0v7h-6z"/>
      <path class="edge" d="M5 8a3 2 0 0 1 6 0v5H5zM13 6a3 2 0 0 1 6 0v7h-6z"/>
      <path class="trimline" d="M5 8a3 2 0 0 0 6 0m2-2a3 2 0 0 0 6 0"/>
    ''',
    "warehouse": '''
      <path class="roof" d="M2.5 13 12 6l9.5 7v2H2.5z"/>
      <path class="edge" d="M2.5 13 12 6l9.5 7"/>
      <path class="trimline" d="M5 13 12 8l7 5"/>
    ''',
    "foundry": '''
      <path class="roof" d="M4 11h16v3H4z"/>
      <path class="edge" d="M4 11h16v3H4z"/>
      <path class="shade" d="M8 5h8v8H8z"/>
      <path class="roof" d="M9 5V3h6v2"/>
      <path class="edge" d="M8 5h8v8H8zM9 3h6"/>
      <path class="trimline" d="M10 7h4v3h-4z"/>
    ''',
    "waterworks": '''
      <path class="shade" d="M8 9v5m8-5v5M7 8h10"/>
      <path class="roof" d="M7 5a5 2 0 0 1 10 0v4H7z"/>
      <path class="edge" d="M7 5a5 2 0 0 1 10 0v4H7zM8 9h8"/>
      <path class="trimline" d="M8 5a4 1.2 0 0 0 8 0"/>
      <path class="roof" d="M4 12h16v2H4z"/>
      <path class="edge" d="M4 12h16v2H4z"/>
    ''',
    "assembly": '''
      <path class="shade" d="M4 6h2v8H4zM18 7h2v7h-2z"/>
      <path class="roof" d="M3 5h17v2H3z"/>
      <path class="edge" d="M3 5h17v2H3zM5 6v7m14-6v7"/>
      <path class="trimline" d="M15 7v3h2v3"/>
      <path class="roof" d="M5 11h14v3H5z"/>
      <path class="edge" d="M5 11h14v3H5z"/>
    ''',
    "refinery": '''
      <path class="roof" d="M4 12h16v2H4z"/>
      <path class="edge" d="M4 12h16v2H4z"/>
      <path class="shade" d="M5 6h4v7H5zM12 4h4v9h-4z"/>
      <path class="edge" d="M5 6h4v7H5zM12 4h4v9h-4z"/>
      <path class="trimline" d="M6 8h2m5-2h2"/>
      <path class="piping" d="M9 8h2v-3h1m4 6h3v-3h2"/>
    ''',
}

THEME_FINISHES = {
    "retro": '<path class="extra" d="M4 12h2v1H4zm13-1h2v1h-2zM7 5h1V4h1V3h1"/>',
    "edo": '<path class="extra" d="M4 10q2-3 4-4M16 6q2 1 4 4"/>',
    "y2k": '<path class="shine" d="M5 14h2v6H5zm2 0h8v1H7z"/>',
    "noir": '<path class="extra" d="M18 3h2v2h-2z"/>',
    "deepsea": '<circle class="glowdot" cx="3" cy="8" r=".65"/><circle class="glowdot" cx="21" cy="6" r=".55"/>',
    "garden": '<path class="extra" d="M3 16q-1-2 0-3m18 4q1-2 0-3"/>',
    "cyber": '<path class="extra" d="M3 9h2V7h2M19 11h2V8h1"/>',
}


def definitions(theme: str, style: dict[str, str]) -> str:
    defs = []
    if theme == "y2k":
        defs.append('''<linearGradient id="wallGradient" x1="0" y1="0" x2="0.8" y2="1">
          <stop offset="0" stop-color="#f9fdff"/><stop offset=".48" stop-color="#b9d1e4"/><stop offset="1" stop-color="#86a9c7"/>
        </linearGradient><linearGradient id="roofGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#effaff"/><stop offset="1" stop-color="#7bb5d6"/>
        </linearGradient>''')
    elif theme == "deepsea":
        defs.append('''<linearGradient id="gelGradient" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#46d9ef" stop-opacity=".88"/><stop offset="1" stop-color="#244a9a" stop-opacity=".84"/>
        </linearGradient>''')
    if theme in {"cyber", "deepsea"}:
        glow = style["extra"]
        defs.append(f'''<filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation=".7" result="blur"/><feFlood flood-color="{glow}" flood-opacity=".75"/>
          <feComposite in2="blur" operator="in"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>''')
    return f"<defs>{''.join(defs)}</defs>" if defs else ""


def stylesheet(theme: str, style: dict[str, str]) -> str:
    stroke_width = "0.8" if theme == "retro" else ("1.15" if theme in {"garden", "deepsea"} else "0.9")
    linecap = "square" if theme in {"retro", "noir"} else "round"
    extra_filter = ' filter="url(#softGlow)"' if theme in {"cyber", "deepsea"} else ""
    stitch = 'stroke-dasharray="1.1 1.3"' if theme == "garden" else ""
    roof_stroke = style["outline"]
    if theme == "deepsea":
        roof_stroke = "#43eaf5"
    return f'''<style>
      .wall {{ fill:{style['wall']}; stroke:{style['outline']}; stroke-width:{stroke_width}; stroke-linejoin:{linecap}; }}
      .roof {{ fill:{style['roof']}; stroke:{style['outline']}; stroke-width:{stroke_width}; stroke-linejoin:{linecap}; }}
      .shade {{ fill:{style['shade']}; stroke:{style['outline']}; stroke-width:{stroke_width}; stroke-linejoin:{linecap}; }}
      .edge {{ fill:none; stroke:{roof_stroke}; stroke-width:{stroke_width}; stroke-linecap:{linecap}; stroke-linejoin:{linecap};{extra_filter} }}
      .trimline {{ fill:none; stroke:{style['trim']}; stroke-width:.65; stroke-linecap:{linecap}; stroke-linejoin:round; }}
      .piping {{ fill:none; stroke:{style['extra']}; stroke-width:.8; stroke-linecap:round; stroke-linejoin:round;{extra_filter} }}
      .window {{ fill:{style['window']}; stroke:{style['outline']}; stroke-width:.55; }}
      .door {{ fill:{style['shade']}; stroke:{style['outline']}; stroke-width:.65; }}
      .signframe {{ fill:{style['shade']}; stroke:{style['outline']}; stroke-width:.7; }}
      .line {{ fill:none; stroke:{style['line']}; stroke-width:.65; stroke-linecap:{linecap}; }}
      .finish {{ fill:none; stroke:{style['trim']}; stroke-width:.55; stroke-linecap:{linecap};{stitch} }}
      .extra {{ fill:none; stroke:{style['extra']}; stroke-width:.8; stroke-linecap:round; stroke-linejoin:round;{extra_filter} }}
      .shine {{ fill:#ffffff; fill-opacity:.72; stroke:none; }}
      .glowdot {{ fill:{style['extra']}; filter:url(#softGlow); }}
    </style>'''


def finish_art(theme: str, style: dict[str, str]) -> str:
    parts = [style["finish"], THEME_FINISHES[theme]]
    if theme == "garden":
        parts.append('<path class="finish" d="M4.5 14.5h15v6.8h-15z"/>')
    elif theme == "cyber":
        parts.append('<path class="piping" d="M5 21h14M19 15h1v3h-2"/>')
    elif theme == "deepsea":
        parts.append('<path class="piping" d="M5 21h14"/>')
    elif theme == "noir":
        parts.append('<path class="line" d="M6 14v7m12-7v7"/>')
    return "".join(parts)


def svg(theme: str, building: str) -> str:
    style = STYLES[theme]
    markup = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="96" height="96" {style['render']}>
      {definitions(theme, style)}
      {stylesheet(theme, style)}
      <g class="factory">
        <path class="wall" d="M4 13h16v9H4z"/>
        <path class="shade" d="M15.8 13H20v9h-4.2z"/>
        <path class="edge" d="M4 13h16M4 22h16"/>
        {UPPERS[building]}
        <path class="window" d="M6.4 15h2.5v2.5H6.4zM15.2 15h2.5v2.5h-2.5z"/>
        <path class="line" d="M7.65 15v2.5m8.8-2.5v2.5"/>
        <path class="door" d="M17 18h2v4h-2z"/>
        <path class="signframe" d="M9.5 16.5h5v3h-5z"/>
        <path class="finish" d="M10 20h4"/>
        {finish_art(theme, style)}
      </g>
    </svg>'''
    return "\n".join(line.rstrip() for line in markup.splitlines()) + "\n"


def generate(theme: str, output_dir: Path | None = None) -> int:
    """Write one SVG per archetype into the selected theme's art directory."""
    if theme not in STYLES:
        raise ValueError(f"unknown theme: {theme}")
    out = output_dir or ROOT / "mods" / "herdr-critters" / "themes" / theme / "art"
    out.mkdir(parents=True, exist_ok=True)
    for building in BUILDINGS:
        (out / f"space-{building}.svg").write_text(svg(theme, building), encoding="utf-8")
    return len(BUILDINGS)


def generate_all() -> int:
    """Write all seven theme sets; return the number of generated files."""
    return sum(generate(theme) for theme in STYLES)
