"""Theme-aware isometric city art for the Spaces section.

One city plate (ground, roads, a park, empty lots) plus one isometric SVG per
factory type. The mod stacks them: the plate first, then each space's building
on its lot, back to front. Every theme draws the same geometry in its own
palette and finish, so a space keeps its building when the theme changes.

Also writes `mods/herdr-critters/city.js`, the geometry the mod needs to place
buildings, flags, the active arrow and agent sprites.
"""

import json
import math
from pathlib import Path

from art.space_factory_art import BUILDINGS

ROOT = Path(__file__).resolve().parent.parent

# Grid: 3 x 3 blocks of B units, roads of R units, an outer margin of M units.
U, V = 10, 5  # px per grid unit: across, down (2:1 isometric)
B, R, M = 3.0, 1.0, 0.5
G = 2 * M + 3 * B + 2 * R  # 12 units a side
W = 240  # canvas width
TOP = 62  # room above the plate for tall buildings, flags and the arrow
T = 10  # plate thickness, px
H = int(TOP + G * U + T + 2)
OX = W / 2
# A building canvas covers one lot plus the height above it.
HT = 60
BW = int(2 * B * U)
BH = int(HT + B * U + 2)

# Lots in back-to-front screen order; (1, 1) is the park.
LOTS = [(0, 0), (0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1), (2, 2)]
PARK = (1, 1)


def lot_origin(i: int, j: int) -> tuple[float, float]:
    return M + i * (B + R), M + j * (B + R)


def P(gx: float, gy: float, z: float = 0) -> tuple[float, float]:
    """City canvas point."""
    return OX + (gx - gy) * U, TOP + (gx + gy) * V - z


def Q(gx: float, gy: float, z: float = 0) -> tuple[float, float]:
    """Building canvas point (lot-local grid)."""
    return B * U + (gx - gy) * U, HT + (gx + gy) * V - z


def pts(points) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def poly(cls: str, points, extra: str = "") -> str:
    return f'<polygon class="{cls}" points="{pts(points)}"{extra}/>'


def line(cls: str, a, b) -> str:
    return f'<line class="{cls}" x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}"/>'


# Palettes. Walls and roofs come in four variants so the city isn't one color;
# each factory type keeps its variant in every theme.
CITY = {
    "retro": dict(
        outline="#241b2e", walls=["#9b6948", "#7a6296", "#a8584a", "#5f7a8c"],
        roofs=["#d27a3c", "#e8922e", "#c4566a", "#4fb8bd"], window="#f5e29a", trim="#f2b94d",
        extra="#5ed8dd", ground="#3b3150", lot="#4b3f63", road="#2a2236", lane="#f2b94d",
        side_l="#34283f", side_r="#241b2e", grass="#4f8a4a", water="#3e6fb0", water_hi="#8fd0f0",
        tree="#5fae5a", tree2="#3c7a3c", trunk="#5c4033", night=True, crisp=True,
    ),
    "edo": dict(
        outline="#292b36", walls=["#e4d4b4", "#d8c6a0", "#efe3c8", "#c9b28a"],
        roofs=["#385b7b", "#2f4a66", "#8a3b2e", "#4a6a52"], window="#d7e0d1", trim="#c74430",
        extra="#b84432", ground="#e9dfc6", lot="#ddcfac", road="#c4ab80", lane="#8a6a48",
        side_l="#9a7a55", side_r="#7a5c3e", grass="#9fb27a", water="#4a7aa0", water_hi="#e9f0f0",
        tree="#eaa6b4", tree2="#6f8f5a", trunk="#4a3428", night=False, crisp=False,
    ),
    "y2k": dict(
        outline="#6e8298", walls=["#e6f1fa", "#cfe3f2", "#f3e6f5", "#d9f2e0"],
        roofs=["#7bb5d6", "#9ad0f0", "#ee7bd7", "#8fd65a"], window="#9fd8ff", trim="#c3f56a",
        extra="#ee7bd7", ground="#dceefa", lot="#f4f9ff", road="#a9c4d8", lane="#ffffff",
        side_l="#8fb0cc", side_r="#6e8eab", grass="#8fd65a", water="#5cc6ff", water_hi="#ffffff",
        tree="#9be05a", tree2="#5fbf3a", trunk="#8a6a4a", night=False, crisp=False,
    ),
    "noir": dict(
        outline="#1c1c20", walls=["#aaa69b", "#8f8c84", "#7a7873", "#b8b3a6"],
        roofs=["#5c5d62", "#47484c", "#6a6b70", "#3b3c41"], window="#e4cb91", trim="#d7cdb5",
        extra="#bb303b", ground="#3a3a3f", lot="#4a4a50", road="#222226", lane="#d7cdb5",
        side_l="#2a2a2e", side_r="#18181b", grass="#34383a", water="#1c1f26", water_hi="#6a6f7a",
        tree="#2a2c2e", tree2="#1f2123", trunk="#111114", night=True, crisp=True,
        sil="#28282d", silside="#1e1e22", siltop="#323238",
    ),
    "deepsea": dict(
        outline="#0b2742", walls=["#2f8fc0", "#3a6fb0", "#4aa6a8", "#5a5fb0"],
        roofs=["#17628a", "#1d4f7a", "#2a7f86", "#3d3f86"], window="#c5ffff", trim="#74ffff",
        extra="#ff8bdf", ground="#0f2c4c", lot="#24405a", road="#0a2038", lane="#53e4ef",
        side_l="#0a1f38", side_r="#061526", grass="#1d5d6a", water="#041427", water_hi="#53e4ef",
        tree="#ff8bdf", tree2="#c86ad0", trunk="#b0507a", night=True, crisp=False,
    ),
    "garden": dict(
        outline="#624936", walls=["#b8483a", "#d9aa72", "#efe6d2", "#c9583f"],
        roofs=["#5f5a55", "#7a4a3a", "#8fa86a", "#6a7480"], window="#f8f2d8", trim="#fff0c9",
        extra="#e07aa5", ground="#b9d58e", lot="#d8e8b0", road="#e8d3a8", lane="#fff0c9",
        side_l="#8a6a48", side_r="#6e5236", grass="#8fbf6a", water="#8fc8e0", water_hi="#ffffff",
        tree="#7fb85a", tree2="#f2a0c0", trunk="#7a5a3a", night=False, crisp=False,
    ),
    "cyber": dict(
        outline="#0b0618", walls=["#302044", "#241a3a", "#3a2050", "#1e2440"],
        roofs=["#45235d", "#2c3a6a", "#5a2060", "#1a4a5a"], window="#39ff90", trim="#00efff",
        extra="#ff37d7", ground="#160d2a", lot="#21133a", road="#0a0616", lane="#ff37d7",
        side_l="#120a22", side_r="#080412", grass="#0f3a3a", water="#04203a", water_hi="#00efff",
        tree="#00efff", tree2="#ff37d7", trunk="#4a2a6a", night=True, crisp=False,
    ),
}
GLOW = {"cyber", "deepsea"}


def shade(color: str, k: float) -> str:
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{max(0, min(255, round(c * k))):02x}" for c in (r, g, b))


def header(theme: str, width: int, height: int, variant: int = 0) -> str:
    c = CITY[theme]
    wall = c["walls"][variant]
    roof = c["roofs"][variant]
    render = 'shape-rendering="crispEdges"' if c["crisp"] else 'shape-rendering="geometricPrecision"'
    sw = 0.8 if theme != "garden" else 0.9
    glow = ' filter:url(#glow);' if theme in GLOW else ""
    stitch = "stroke-dasharray:1.4 1.2;" if theme == "garden" else ""
    defs = ""
    if theme in GLOW:
        defs = f'''<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="1" result="b"/><feFlood flood-color="{c['extra']}" flood-opacity=".8"/>
      <feComposite in2="b" operator="in"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter></defs>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" {render}>
    {defs}
    <style>
      polygon, path, ellipse {{ stroke:{c['outline']}; stroke-width:{sw}; stroke-linejoin:round; }}
      .wall {{ fill:{wall}; }}
      .shade {{ fill:{shade(wall, 0.68)}; }}
      .roof {{ fill:{roof}; }}
      .roofshade {{ fill:{shade(roof, 0.72)}; }}
      .metal {{ fill:{shade(c['walls'][(variant + 1) % 4], 0.92)}; }}
      .metalshade {{ fill:{shade(c['walls'][(variant + 1) % 4], 0.62)}; }}
      .win {{ fill:{c['window']}; stroke-width:.45; }}
      .windim {{ fill:{shade(c['window'], 0.78)}; stroke-width:.45; }}
      .door {{ fill:{shade(wall, 0.45)}; stroke-width:.5; }}
      .ground {{ fill:{c['ground']}; }}
      .lot {{ fill:{c['lot']}; stroke-width:.5; {stitch} }}
      .road {{ fill:{c['road']}; stroke:none; }}
      .sidel {{ fill:{c['side_l']}; }}
      .sider {{ fill:{c['side_r']}; }}
      .grass {{ fill:{c['grass']}; stroke-width:.5; }}
      .water {{ fill:{c['water']}; stroke-width:.5; }}
      .tree {{ fill:{c['tree']}; stroke-width:.6; }}
      .tree2 {{ fill:{c['tree2']}; stroke-width:.6; }}
      line {{ stroke-linecap:round; }}
      .lane {{ stroke:{c['lane']}; stroke-width:.8; stroke-dasharray:3 3;{glow} }}
      .rim {{ stroke:{c['extra'] if theme in GLOW else c['water_hi']}; stroke-width:.8;{glow} }}
      .trunk {{ stroke:{c['trunk']}; stroke-width:1.2; }}
      .leg {{ stroke:{shade(c['trim'], 0.8)}; stroke-width:1.4; }}
      .fence {{ stroke:{c['trim']}; stroke-width:.7; stroke-dasharray:1.5 1.5; fill:none; }}
      .edge {{ stroke:{c['outline']}; stroke-width:.8; }}
      .trimline {{ stroke:{c['trim']}; stroke-width:.9; fill:none; }}
      .accent {{ stroke:{c['extra']}; stroke-width:1; fill:none;{glow} }}
      .crane {{ fill:{c['trim']}; stroke-width:.5; }}
      .craneshade {{ fill:{shade(c['trim'], 0.7)}; stroke-width:.5; }}
      .accentfill {{ fill:{c['extra']}; stroke-width:.4;{glow} }}
      .brick {{ stroke:{shade(c['side_l'], 0.7)}; stroke-width:.6; }}
      .hi {{ stroke:{c['water_hi']}; stroke-width:.7; fill:none; }}
      .winc {{ fill:{c['trim']}; stroke-width:.4;{glow} }}
      .wine {{ fill:{c['extra']}; stroke-width:.4;{glow} }}
      .windark {{ fill:{shade(c['walls'][variant], 0.4)}; stroke-width:.4; }}
      .neon {{ stroke:{c['extra']}; stroke-width:.9; fill:none;{glow} }}
      .neon2 {{ stroke:{c['trim']}; stroke-width:.9; fill:none;{glow} }}
      .holo {{ fill:{c['trim']}; fill-opacity:.45; stroke:{c['trim']}; stroke-width:.5;{glow} }}
      .glass {{ fill:{c['water_hi']}; fill-opacity:.13; stroke:{c['trim']}; stroke-opacity:.75; stroke-width:.8; }}
      .glassline {{ stroke:#ffffff; stroke-opacity:.45; stroke-width:.8; fill:none; }}
      .ring {{ stroke:{c['trim']}; stroke-width:1.3; fill:none; }}
      .fire {{ stroke:{shade(c['trim'], 0.55)}; stroke-width:.55; fill:none; }}
      .plank {{ stroke:{shade(wall, 0.6)}; stroke-width:.4; stroke-opacity:.8; }}
      .soil {{ fill:#9a7350; stroke-width:.5; }}
      .wheat {{ stroke:#e6c35c; stroke-width:1.1; }}
      .pumpkin {{ fill:#e8823a; stroke-width:.5; }}
      .vine {{ stroke:#5f8f3e; stroke-width:.9; fill:none; }}
      .hay {{ fill:#e8c870; stroke-width:.5; }}
      .rock {{ fill:{shade(c['ground'], 1.6)}; stroke-width:.5; }}
      .sil {{ fill:{c.get('sil', shade(c['ground'], 1.25))}; stroke:{shade(c['ground'], 0.7)}; stroke-width:.5; }}
      .silside {{ fill:{c.get('silside', shade(c['ground'], 0.95))}; stroke:{shade(c['ground'], 0.7)}; stroke-width:.5; }}
      .siltop {{ fill:{c.get('siltop', shade(c['ground'], 1.5))}; stroke:{shade(c['ground'], 0.7)}; stroke-width:.5; }}
      .beam {{ fill:#efe8d0; fill-opacity:.07; stroke:none; }}
      .shaft {{ fill:{c['water_hi']}; fill-opacity:.05; stroke:none; }}
      .fog {{ fill:#9a978c; fill-opacity:.13; stroke:none; }}
      .rut {{ stroke:{shade(c['road'], 0.82)}; stroke-width:.7; }}
      .post {{ stroke:#7a5a3a; stroke-width:1; }}
      .rail {{ stroke:#9a7350; stroke-width:.7; }}
    </style>
'''


# ---------- building primitives (lot-local grid) ----------

class Art:
    def __init__(self):
        self.parts: list[str] = []
        self.top = BH
        self.boxes: list[tuple] = []  # (x0, y0, x1, y1, z0, h) of every box, for theme details

    def note(self, *points):
        for _, y in points:
            self.top = min(self.top, y)

    def add(self, s: str):
        self.parts.append(s)

    def box(self, x0, y0, x1, y1, z0, h, top="roof", left="wall", right="shade"):
        z1 = z0 + h
        self.boxes.append((x0, y0, x1, y1, z0, h))
        t = [Q(x0, y0, z1), Q(x1, y0, z1), Q(x1, y1, z1), Q(x0, y1, z1)]
        lf = [Q(x0, y1, z0), Q(x1, y1, z0), Q(x1, y1, z1), Q(x0, y1, z1)]
        rf = [Q(x1, y0, z0), Q(x1, y1, z0), Q(x1, y1, z1), Q(x1, y0, z1)]
        self.add(poly(left, lf))
        self.add(poly(right, rf))
        self.add(poly(top, t))
        self.note(*t)

    def windows(self, face, a0, a1, fixed, z0, z1, cols, rows, cls=None):
        """Window grid on the left face (gy = fixed, along gx) or right face (gx = fixed, along gy)."""
        cls = cls or ("win" if face == "left" else "windim")
        aw = (a1 - a0) / cols
        zh = (z1 - z0) / rows
        for c in range(cols):
            for r in range(rows):
                s0, s1 = a0 + aw * (c + 0.25), a0 + aw * (c + 0.75)
                t0, t1 = z0 + zh * (r + 0.25), z0 + zh * (r + 0.75)
                if face == "left":
                    q = [Q(s0, fixed, t0), Q(s1, fixed, t0), Q(s1, fixed, t1), Q(s0, fixed, t1)]
                else:
                    q = [Q(fixed, s0, t0), Q(fixed, s1, t0), Q(fixed, s1, t1), Q(fixed, s0, t1)]
                self.add(poly(cls, q))

    def door(self, face, a0, a1, fixed, h):
        if face == "left":
            q = [Q(a0, fixed, 0), Q(a1, fixed, 0), Q(a1, fixed, h), Q(a0, fixed, h)]
        else:
            q = [Q(fixed, a0, 0), Q(fixed, a1, 0), Q(fixed, a1, h), Q(fixed, a0, h)]
        self.add(poly("door", q))

    def gable(self, x0, y0, x1, y1, z, hr):
        ym = (y0 + y1) / 2
        back = [Q(x0, y0, z), Q(x1, y0, z), Q(x1, ym, z + hr), Q(x0, ym, z + hr)]
        front = [Q(x0, y1, z), Q(x1, y1, z), Q(x1, ym, z + hr), Q(x0, ym, z + hr)]
        end = [Q(x1, y0, z), Q(x1, y1, z), Q(x1, ym, z + hr)]
        self.add(poly("roofshade", back))
        self.add(poly("shade", end))
        self.add(poly("roof", front))
        self.note(*front)

    def cylinder(self, cx, cy, r, z0, h, body="metal", body_shade="metalshade", cap="roof", dome=0.0, bands=()):
        x, yb = Q(cx, cy, z0)
        yt = yb - h
        rx = math.sqrt(2) * r * U
        ry = rx / 2
        xl, xr = x - rx, x + rx
        self.add(f'<path class="{body}" d="M{xl:.2f} {yt:.2f}L{xl:.2f} {yb:.2f}A{rx:.2f} {ry:.2f} 0 0 0 {xr:.2f} {yb:.2f}L{xr:.2f} {yt:.2f}Z"/>')
        self.add(f'<path class="{body_shade}" d="M{x:.2f} {yt + ry:.2f}L{x:.2f} {yb + ry:.2f}A{rx:.2f} {ry:.2f} 0 0 0 {xr:.2f} {yb:.2f}L{xr:.2f} {yt:.2f}Z" style="stroke:none"/>')
        self.add(f'<path class="{body}" d="M{xl:.2f} {yt:.2f}L{xl:.2f} {yb:.2f}A{rx:.2f} {ry:.2f} 0 0 0 {xr:.2f} {yb:.2f}L{xr:.2f} {yt:.2f}" style="fill:none"/>')
        for f in bands:
            yy = yb - h * f
            self.add(f'<path class="trimline" d="M{xl:.2f} {yy:.2f}A{rx:.2f} {ry:.2f} 0 0 0 {xr:.2f} {yy:.2f}"/>')
        if dome:
            rd = ry + dome
            self.add(f'<path class="{cap}" d="M{xl:.2f} {yt:.2f}A{rx:.2f} {rd:.2f} 0 0 1 {xr:.2f} {yt:.2f}A{rx:.2f} {ry:.2f} 0 0 1 {xl:.2f} {yt:.2f}Z"/>')
            self.note((x, yt - rd))
        else:
            self.add(f'<ellipse class="{cap}" cx="{x:.2f}" cy="{yt:.2f}" rx="{rx:.2f}" ry="{ry:.2f}"/>')
            self.note((x, yt - ry))

    def stroke(self, cls, *points):
        d = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in points)
        self.add(f'<path class="{cls}" d="{d}" style="fill:none"/>')
        self.note(*points)


# Each building returns its flag point (lot-local grid x, y, z): the roof spot
# where the mod plants the space's color flag.

def mill(a: Art):
    a.box(0.4, 0.7, 2.6, 2.6, 0, 15)
    a.windows("left", 0.4, 2.6, 2.6, 2, 13, 4, 2)
    a.windows("right", 0.7, 2.6, 2.6, 2, 13, 3, 2)
    a.door("left", 1.3, 1.7, 2.6, 6)
    teeth = 3
    w = 2.2 / teeth
    for k in range(teeth):
        xa, xb = 0.4 + k * w, 0.4 + (k + 1) * w
        z, hr = 15, 7
        a.add(poly("roof", [Q(xa, 0.7, z), Q(xb, 0.7, z + hr), Q(xb, 2.6, z + hr), Q(xa, 2.6, z)]))
        a.add(poly("win", [Q(xb, 0.7, z), Q(xb, 2.6, z), Q(xb, 2.6, z + hr), Q(xb, 0.7, z + hr)]))
        a.add(poly("wall", [Q(xa, 2.6, z), Q(xb, 2.6, z), Q(xb, 2.6, z + hr)]))
        a.note(Q(xb, 0.7, z + hr))
    return (1.1, 1.6, 18.5)


def power(a: Art):
    a.cylinder(1.0, 0.55, 0.28, 0, 40, bands=(0.82, 0.9))
    a.box(0.3, 1.0, 2.1, 2.6, 0, 14)
    a.windows("left", 0.3, 2.1, 2.6, 3, 12, 3, 2)
    a.windows("right", 1.0, 2.6, 2.1, 3, 12, 2, 2)
    a.door("left", 0.8, 1.2, 2.6, 6)
    a.cylinder(2.4, 1.2, 0.3, 0, 48, bands=(0.84, 0.92))
    return (1.2, 1.8, 14)


def tank(a: Art):
    a.box(0.3, 0.3, 2.7, 2.7, 0, 4, top="roofshade")
    a.cylinder(1.95, 0.95, 0.58, 4, 20, body="wall", body_shade="shade", dome=5, bands=(0.5,))
    a.stroke("accent", Q(1.5, 1.5, 9), Q(1.5, 1.5, 4))
    a.stroke("accent", Q(1.25, 1.25, 9), Q(1.75, 1.25, 9))
    a.cylinder(0.95, 1.95, 0.5, 4, 14, body="wall", body_shade="shade", dome=4, bands=(0.5,))
    return (1.95, 0.95, 30)


def warehouse(a: Art):
    a.box(0.4, 0.5, 2.6, 2.6, 0, 13)
    a.windows("left", 0.4, 2.6, 2.6, 7, 12, 5, 1)
    a.door("left", 0.7, 1.3, 2.6, 6)
    a.door("left", 1.7, 2.3, 2.6, 6)
    a.windows("right", 0.5, 2.6, 2.6, 2, 11, 2, 1)
    a.gable(0.4, 0.5, 2.6, 2.6, 13, 9)
    return (1.4, 1.55, 22)


def foundry(a: Art):
    a.box(0.8, 0.35, 1.9, 1.3, 0, 27)
    a.windows("right", 0.35, 1.3, 1.9, 14, 25, 1, 2)
    a.cylinder(1.4, 0.7, 0.17, 27, 12, bands=(0.75,))
    a.box(0.3, 1.3, 2.7, 2.6, 0, 11)
    a.windows("left", 0.3, 2.7, 2.6, 2, 10, 4, 1)
    fire = [Q(1.8, 2.6, 0.5), Q(2.4, 2.6, 0.5), Q(2.4, 2.6, 6), Q(1.8, 2.6, 6)]
    a.add(poly("accentfill", fire))
    a.windows("right", 1.3, 2.6, 2.7, 2, 9, 2, 1)
    return (1.35, 0.85, 27)


def waterworks(a: Art):
    cx, cy, z = 1.2, 0.9, 24
    for dx, dy in ((-0.4, -0.4), (0.4, -0.4), (-0.4, 0.4), (0.4, 0.4)):
        a.add(line("leg", Q(cx + dx, cy + dy, 0), Q(cx + dx * 0.8, cy + dy * 0.8, z)))
    a.add(line("trimline", Q(cx - 0.4, cy + 0.4, 10), Q(cx + 0.4, cy + 0.4, 10)))
    a.add(line("trimline", Q(cx + 0.4, cy - 0.4, 10), Q(cx + 0.4, cy + 0.4, 10)))
    a.cylinder(cx, cy, 0.62, z, 11, body="wall", body_shade="shade", dome=4, bands=(0.5,))
    a.box(0.3, 1.5, 2.7, 2.6, 0, 9)
    a.windows("left", 0.3, 2.7, 2.6, 2, 8, 5, 1)
    a.windows("right", 1.5, 2.6, 2.7, 2, 8, 2, 1)
    a.cylinder(0.6, 2.2, 0.13, 9, 7, bands=(0.7,))
    return (2.3, 2.1, 9)


def assembly(a: Art):
    a.box(2.42, 0.32, 2.66, 0.56, 0, 36, top="crane", left="crane", right="craneshade")
    a.box(0.55, 0.36, 2.42, 0.52, 34, 2.5, top="crane", left="crane", right="craneshade")
    a.add(line("edge", Q(0.95, 0.44, 34), Q(0.95, 0.44, 24)))
    a.box(0.8, 0.3, 1.1, 0.6, 20, 4, top="roof", left="metal", right="metalshade")
    a.box(0.3, 0.9, 2.7, 2.5, 0, 12)
    a.windows("left", 0.3, 2.7, 2.5, 2, 11, 5, 1)
    a.windows("right", 0.9, 2.5, 2.7, 2, 11, 3, 1)
    a.box(0.6, 1.1, 1.9, 2.2, 12, 8, top="roof", left="metal", right="metalshade")
    a.windows("left", 0.6, 1.9, 2.2, 13, 19, 3, 1)
    return (1.25, 1.65, 20)


def refinery(a: Art):
    a.box(0.3, 0.3, 2.7, 2.7, 0, 4, top="roofshade")
    a.cylinder(0.9, 0.9, 0.3, 4, 36, bands=(0.3, 0.6, 0.9))
    a.cylinder(1.9, 0.75, 0.34, 4, 26, bands=(0.4, 0.8))
    a.stroke("accent", Q(1.15, 1.15, 22), Q(1.55, 0.95, 22), Q(1.55, 0.95, 18))
    x, y = Q(0.9, 0.9, 40)
    a.add(f'<path class="accentfill" d="M{x - 1.6:.2f} {y + 1:.2f}Q{x:.2f} {y - 6:.2f} {x + 1.6:.2f} {y + 1:.2f}Z"/>')
    a.note((x, y - 6))
    a.cylinder(1.95, 1.95, 0.5, 4, 9, body="wall", body_shade="shade", dome=4, bands=(0.5,))
    a.stroke("accent", Q(1.2, 1.4, 8), Q(1.45, 1.95, 8))
    return (1.95, 1.95, 17)


def lot_tree(a: Art, theme: str, gx: float, gy: float, kind: int, size: float = 1.0):
    """One tree at a lot-local grid point: round, pine or tall, scaled by `size`."""
    c = CITY[theme]
    x, y = Q(gx, gy)
    if theme == "deepsea":  # kelp and coral instead of trees
        h = 6 * size
        a.add(f'<path class="accent" d="M{x:.1f} {y:.1f}q-2 {-h * 0.6:.1f} 0 {-h:.1f}q2 {-h * 0.5:.1f} 0 {-h:.1f}" style="stroke:{c["tree" if kind % 2 else "tree2"]}"/>')
        a.note((x, y - 2 * h))
        return
    trunk = 3.5 * size
    a.add(f'<line class="trunk" x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y - trunk:.1f}"/>')
    cls = "tree2" if kind == 1 else "tree"
    if kind == 1:  # pine
        w, h = 3.6 * size, 10 * size
        a.add(f'<path class="{cls}" d="M{x - w:.1f} {y - trunk + 1:.1f}L{x:.1f} {y - h:.1f}L{x + w:.1f} {y - trunk + 1:.1f}Z"/>')
        a.note((x, y - h))
    elif kind == 2:  # tall
        rx, ry = 2.6 * size, 4.4 * size
        a.add(f'<ellipse class="{cls}" cx="{x:.1f}" cy="{y - trunk - ry + 1:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"/>')
        a.note((x, y - trunk - 2 * ry))
    else:  # round
        rx, ry = 3.6 * size, 3.1 * size
        a.add(f'<ellipse class="{cls}" cx="{x:.1f}" cy="{y - trunk - ry + 1:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"/>')
        a.note((x, y - trunk - 2 * ry))


def trees(a: Art, theme: str, spots):
    """Trees drawn back to front: [(gx, gy, kind, size), ...]."""
    for gx, gy, kind, size in sorted(spots, key=lambda t: t[0] + t[1]):
        lot_tree(a, theme, gx, gy, kind, size)


def grass_patch(a: Art, x0, y0, x1, y1):
    a.add(poly("grass", [Q(x0, y0), Q(x1, y0), Q(x1, y1), Q(x0, y1)]))


def empty_grove(a: Art, theme: str):
    grass_patch(a, 0.3, 0.3, 2.7, 2.7)
    trees(a, theme, [
        (0.6, 0.6, 1, 1.1), (1.5, 0.5, 0, 1.0), (2.4, 0.7, 2, 1.0), (0.7, 1.5, 0, 0.9),
        (1.6, 1.4, 1, 1.25), (2.4, 1.7, 0, 0.85), (0.6, 2.4, 2, 0.9), (1.5, 2.3, 0, 1.0),
        (2.35, 2.45, 1, 0.8),
    ])


def empty_park(a: Art, theme: str):
    c = CITY[theme]
    grass_patch(a, 0.3, 0.3, 2.7, 2.7)
    # a path across, a bench and a little fountain
    a.add(poly("lot", [Q(1.3, 0.3), Q(1.7, 0.3), Q(1.7, 2.7), Q(1.3, 2.7)]))
    x, y = Q(1.5, 1.5)
    a.add(f'<ellipse class="water" cx="{x:.1f}" cy="{y:.1f}" rx="5" ry="2.5"/>')
    a.add(f'<path class="hi" d="M{x:.1f} {y - 1:.1f}v-3"/>')
    a.box(2.0, 2.0, 2.5, 2.15, 1.5, 1.5, top="roof", left="door", right="door")
    trees(a, theme, [(0.6, 0.6, 0, 1.15), (2.4, 0.6, 2, 1.0), (0.6, 2.3, 1, 1.0), (2.4, 1.3, 0, 0.8)])


def empty_orchard(a: Art, theme: str):
    grass_patch(a, 0.3, 0.3, 2.7, 2.7)
    for k in range(3):
        g = 0.75 + k * 0.75
        a.add(line("hi", Q(0.4, g + 0.3), Q(2.6, g + 0.3)))
    trees(a, theme, [(0.7 + i * 0.8, 0.7 + j * 0.8, 0, 0.75) for i in range(3) for j in range(3)])


def empty_plot(a: Art, theme: str):
    """A fenced plot with a sign post: room for a new space."""
    c = CITY[theme]
    a.add(poly("fence", [Q(0.35, 0.35), Q(2.65, 0.35), Q(2.65, 2.65), Q(0.35, 2.65)]))
    trees(a, theme, [(0.7, 0.7, 0, 1.0), (2.2, 0.75, 1, 1.0), (0.75, 2.2, 2, 0.9), (1.3, 0.55, 0, 0.7)])
    x, y = Q(1.9, 1.9)
    a.add(line("edge", (x, y), (x, y - 9)))
    a.add(f'<rect class="crane" x="{x - 4:.1f}" y="{y - 14:.1f}" width="8" height="6" style="stroke:{c["outline"]}"/>')
    a.add(line("edge", (x - 1.8, y - 11), (x + 1.8, y - 11)))
    a.add(line("edge", (x, y - 12.8), (x, y - 9.2)))


EMPTY = [empty_grove, empty_plot, empty_park, empty_orchard]


DRAW = {
    "mill": mill, "power": power, "tank": tank, "warehouse": warehouse,
    "foundry": foundry, "waterworks": waterworks, "assembly": assembly, "refinery": refinery,
}


# Where a working space's smoke rises: a chimney, stack or roof vent (lot-local grid x, y, z).
SMOKE = {
    "mill": (2.2, 0.9, 22), "power": (2.4, 1.2, 50), "tank": (1.95, 0.95, 30),
    "warehouse": (1.8, 1.55, 22), "foundry": (1.4, 0.7, 40), "waterworks": (0.6, 2.2, 17),
    "assembly": (1.25, 1.65, 20), "refinery": (0.9, 0.9, 46),
}


def building_svg(theme: str, building: str) -> tuple[str, dict]:
    a = Art()
    fx, fy, fz = DRAW[building](a)
    from art import city_dress
    if theme in city_dress.BUILDING:
        city_dress.BUILDING[theme](a, building)
    flag = Q(fx, fy, fz)
    variant = BUILDINGS.index(building) % 4
    body = header(theme, BW, BH, variant) + "  " + "\n  ".join(a.parts) + "\n</svg>\n"
    smoke = Q(*SMOKE[building])
    return body, {
        "flag": [round(flag[0], 1), round(flag[1], 1)],
        "smoke": [round(smoke[0], 1), round(smoke[1], 1)],
        "top": round(a.top, 1),
    }


# ---------- the plate ----------

def tree(parts, c, gx, gy, theme, k=0):
    x, y = P(gx, gy)
    cls = "tree" if k % 3 else "tree2"
    if theme == "deepsea":
        parts.append(f'<path class="accent" d="M{x:.1f} {y:.1f}q-2 -4 0 -7q2 -3 0 -6" style="stroke:{c["tree" if k % 2 else "tree2"]}"/>')
        return
    parts.append(line("trunk", (x, y), (x, y - 4)))
    if theme == "edo" and k % 2 == 0:
        parts.append(f'<path class="tree2" d="M{x - 4:.1f} {y - 3:.1f}L{x:.1f} {y - 11:.1f}L{x + 4:.1f} {y - 3:.1f}Z"/>')
    else:
        parts.append(f'<ellipse class="{cls}" cx="{x:.1f}" cy="{y - 6:.1f}" rx="3.6" ry="3.2"/>')


def lamp(parts, c, gx, gy):
    x, y = P(gx, gy)
    parts.append(line("edge", (x, y), (x, y - 9)))
    parts.append(f'<circle cx="{x:.1f}" cy="{y - 9.5:.1f}" r="1.3" style="fill:{c["window"]};stroke:none"/>')
    parts.append(f'<circle cx="{x:.1f}" cy="{y - 9.5:.1f}" r="3.2" style="fill:{c["window"]};fill-opacity:.22;stroke:none"/>')


def plate_svg(theme: str) -> str:
    from art import city_dress
    c = CITY[theme]
    p = []
    if theme in city_dress.PLATE_BACK:
        city_dress.PLATE_BACK[theme](p, theme)
    # sides
    p.append(poly("sidel", [P(0, G, 0), P(G, G, 0), P(G, G, -T), P(0, G, -T)]))
    p.append(poly("sider", [P(G, 0, 0), P(G, G, 0), P(G, G, -T), P(G, 0, -T)]))
    if theme in {"retro", "noir"}:
        for z in (-3.5, -7):
            p.append(line("brick", P(0, G, z), P(G, G, z)))
            p.append(line("brick", P(G, 0, z), P(G, G, z)))
    # ground
    p.append(poly("ground", [P(0, 0), P(G, 0), P(G, G), P(0, G)]))
    # roads
    for k in (1, 2):
        a = M + k * B + (k - 1) * R
        p.append(poly("road", [P(0, a), P(G, a), P(G, a + R), P(0, a + R)]))
        p.append(poly("road", [P(a, 0), P(a + R, 0), P(a + R, G), P(a, G)]))
    for k in (1, 2):
        if theme in city_dress.NO_LANES:
            break
        mid = M + k * B + (k - 1) * R + R / 2
        p.append(line("lane", P(0.2, mid), P(G - 0.2, mid)))
        p.append(line("lane", P(mid, 0.2), P(mid, G - 0.2)))
    # lots
    for i in range(3):
        for j in range(3):
            x0, y0 = lot_origin(i, j)
            cls = "grass" if (i, j) == PARK else "lot"
            p.append(poly(cls, [P(x0, y0), P(x0 + B, y0), P(x0 + B, y0 + B), P(x0, y0 + B)]))
    # park: pond and trees
    x0, y0 = lot_origin(*PARK)
    cx, cy = P(x0 + 1.6, y0 + 1.6)
    p.append(f'<ellipse class="water" cx="{cx:.1f}" cy="{cy:.1f}" rx="11" ry="5.5"/>')
    p.append(f'<path class="hi" d="M{cx - 6:.1f} {cy - 1:.1f}q3 -1.5 6 0M{cx + 1:.1f} {cy + 2:.1f}q2.5 -1.2 5 0"/>')
    for k, (dx, dy) in enumerate(((0.4, 0.5), (2.5, 0.5), (0.5, 2.5), (2.6, 2.3), (1.5, 0.3))):
        tree(p, c, x0 + dx, y0 + dy, theme, k)
    # rim and theme finishes
    if theme in {"y2k", "cyber", "deepsea"}:
        p.append(line("rim", P(0, G), P(G, G)))
        p.append(line("rim", P(G, 0), P(G, G)))
    if theme in {"noir", "cyber", "retro"}:
        for k1 in (1, 2):
            for k2 in (1, 2):
                a = M + k1 * B + (k1 - 1) * R - 0.15
                b = M + k2 * B + (k2 - 1) * R - 0.15
                lamp(p, c, a, b)
    if theme == "deepsea":
        for bx, by, r in ((30, 40, 1.6), (36, 30, 1.1), (210, 50, 1.4), (204, 38, 0.9), (120, 20, 1.2)):
            p.append(f'<circle class="hi" cx="{bx}" cy="{by}" r="{r}"/>')
    if theme == "garden":
        for k, (gx, gy) in enumerate(((0.25, 2.0), (0.25, 7.5), (2.0, 0.25), (7.5, 0.25), (11.75, 6), (6, 11.75))):
            x, y = P(gx, gy)
            p.append(f'<circle cx="{x:.1f}" cy="{y - 1:.1f}" r="1.4" style="fill:{c["tree2"] if k % 2 else c["window"]};stroke-width:.4"/>')
    if theme == "edo":
        x, y = P(G, G)
        p.append(line("trimline", P(0, G, -T / 2), P(G, G, -T / 2)))
    if theme in city_dress.PLATE_FRONT:
        city_dress.PLATE_FRONT[theme](p, theme)
    return header(theme, W, H) + "  " + "\n  ".join(p) + "\n</svg>\n"


def geometry(meta: dict) -> dict:
    lots = []
    for i, j in LOTS:
        x0, y0 = lot_origin(i, j)
        px, py = P(x0, y0)
        fx, fy = P(x0 + B, y0 + B)
        lots.append({"x": round(px - B * U), "y": round(py - HT), "front": [round(fx), round(fy)]})
    return {
        "canvas": {"w": W, "h": H},
        "empties": len(EMPTY),
        "building": {"w": BW, "h": BH, "top": HT},
        "lots": lots,
        "types": meta,
    }


def generate(theme: str, output_dir: Path | None = None) -> int:
    if theme not in CITY:
        raise ValueError(f"unknown theme: {theme}")
    out = output_dir or ROOT / "mods" / "herdr-critters" / "themes" / theme / "art"
    out.mkdir(parents=True, exist_ok=True)
    (out / "city-plate.svg").write_text(plate_svg(theme), encoding="utf-8")
    from art import city_dress
    for k, draw in enumerate(city_dress.EMPTY.get(theme, EMPTY)):
        a = Art()
        draw(a, theme)
        (out / f"city-empty-{k}.svg").write_text(header(theme, BW, BH) + "  " + "\n  ".join(a.parts) + "\n</svg>\n", encoding="utf-8")
    old = out / "city-empty.svg"
    if old.exists():
        old.unlink()
    meta = {}
    for building in BUILDINGS:
        text, meta[building] = building_svg(theme, building)
        (out / f"city-{building}.svg").write_text(text, encoding="utf-8")
    js = "// Generated by art/space_city_art.py. Isometric city geometry, px.\nexport default "
    (ROOT / "mods" / "herdr-critters" / "city.js").write_text(js + json.dumps(geometry(meta), indent=1) + ";\n", encoding="utf-8")
    return 1 + len(EMPTY) + len(BUILDINGS)


def generate_all() -> int:
    return sum(generate(theme) for theme in CITY)


if __name__ == "__main__":
    print(f"wrote {generate_all()} city files")
