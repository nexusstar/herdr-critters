"""Per-theme character for the isometric city (see art/space_city_art.py).

Four themes get their own city on top of the shared geometry:

- cyber: a neon megacity. Neon edges, wall signs, holo billboards and
  antennas on the buildings; a dim tower skyline behind the plate; filler
  towers and a holo plaza on empty lots.
- noir: a gothic city at night. Cornice ledges, fire escapes and rooftop water
  tanks; a skyline of spires and stepped towers under a moon, searchlight
  beams, fog and wet streets; tenements, a church and a bare park on empty lots.
- deepsea: an underwater habitat. Every building sits under a glass dome;
  glass tubes run along the roads; light shafts, rocks and kelp; reefs, pods
  and kelp forests on empty lots.
- garden: farmland. Red barns with planks and X doors, a windmill, hay bales,
  dirt roads with ruts and a fence; wheat, pumpkins and vegetable rows on
  empty lots.

The hooks: BUILDING[theme](art, building) adds details after a building is
drawn; PLATE_BACK / PLATE_FRONT[theme](parts, theme) draw behind and over the
plate; EMPTY[theme] lists the four empty-lot designs; NO_LANES drops the lane
dashes.
"""

import random

from art.space_city_art import (
    B, CITY, G, M, PARK, R, TOP, W, Art, P, Q, empty_plot, grass_patch, line,
    lot_origin, poly, trees,
)


# ---------- helpers ----------

def iso_box(parts, proj, x0, y0, x1, y1, z0, h, top="siltop", left="sil", right="silside"):
    z1 = z0 + h
    parts.append(poly(left, [proj(x0, y1, z0), proj(x1, y1, z0), proj(x1, y1, z1), proj(x0, y1, z1)]))
    parts.append(poly(right, [proj(x1, y0, z0), proj(x1, y1, z0), proj(x1, y1, z1), proj(x1, y0, z1)]))
    parts.append(poly(top, [proj(x0, y0, z1), proj(x1, y0, z1), proj(x1, y1, z1), proj(x0, y1, z1)]))


def face_dots(parts, proj, face, a0, a1, fixed, z0, z1, rng, frac, colors, opacity=0.75):
    """Scattered lit windows on a face: small quads, `frac` of the grid lit."""
    cols = max(1, int((a1 - a0) / 0.28))
    rows = max(1, int((z1 - z0) / 4))
    for c in range(cols):
        for r in range(rows):
            if rng.random() > frac:
                continue
            s0 = a0 + (a1 - a0) * (c + 0.3) / cols
            s1 = a0 + (a1 - a0) * (c + 0.7) / cols
            t0 = z0 + (z1 - z0) * (r + 0.3) / rows
            t1 = z0 + (z1 - z0) * (r + 0.65) / rows
            if face == "left":
                q = [proj(s0, fixed, t0), proj(s1, fixed, t0), proj(s1, fixed, t1), proj(s0, fixed, t1)]
            else:
                q = [proj(fixed, s0, t0), proj(fixed, s1, t0), proj(fixed, s1, t1), proj(fixed, s0, t1)]
            parts.append(poly("x", q, f' style="fill:{rng.choice(colors)};fill-opacity:{opacity};stroke:none"'))


def biggest(a: Art):
    """The largest box drawn (by volume), or None."""
    return max(a.boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]) * b[5], default=None)


def tallest(a: Art):
    return max(a.boxes, key=lambda b: b[4] + b[5], default=None)


def path(cls, d, style=""):
    return f'<path class="{cls}" d="{d}"{f" style={chr(34)}{style}{chr(34)}" if style else ""}/>'


def pyramid(a: Art, x0, y0, x1, y1, z, h, left="roof", right="roofshade"):
    apex = Q((x0 + x1) / 2, (y0 + y1) / 2, z + h)
    a.add(poly(left, [Q(x0, y1, z), Q(x1, y1, z), apex]))
    a.add(poly(right, [Q(x1, y0, z), Q(x1, y1, z), apex]))
    a.note(apex)


def rooftop_tank(a: Art, gx, gy, z):
    """A wooden water tank on legs, the old-city rooftop kind."""
    for dx, dy in ((-0.15, 0.15), (0.15, 0.15), (0.15, -0.15)):
        a.add(line("fire", Q(gx + dx, gy + dy, z), Q(gx + dx, gy + dy, z + 4)))
    a.cylinder(gx, gy, 0.22, z + 4, 6, body="wall", body_shade="shade", cap="roof", dome=2.5, bands=(0.35, 0.7))


# ---------- cyber ----------

def cyber_building(a: Art, building: str):
    for x0, y0, x1, y1, z0, h in list(a.boxes):
        if h < 6:
            continue
        z1 = z0 + h
        a.stroke("neon", Q(x0, y1, z1), Q(x1, y1, z1), Q(x1, y0, z1))
        a.add(line("neon2", Q(x0, y1, z0 + 0.6), Q(x1, y1, z0 + 0.6)))
    big = biggest(a)
    if big:
        x0, y0, x1, y1, z0, h = big
        z1 = z0 + h
        # a vertical sign on the left face and a holo billboard on the right
        s0, s1 = x0 + 0.18, x0 + 0.38
        top = min(z1 - 1, z0 + 15)
        a.add(poly("winc", [Q(s0, y1, z0 + 3), Q(s1, y1, z0 + 3), Q(s1, y1, top), Q(s0, y1, top)]))
        for t in range(int(z0 + 5), int(top) - 1, 3):
            a.add(line("windark", Q(s0 + 0.04, y1, t), Q(s1 - 0.04, y1, t)))
        if y1 - y0 > 0.9:
            a.add(poly("holo", [Q(x1, y0 + 0.25, z1 - 7), Q(x1, y0 + 0.95, z1 - 7), Q(x1, y0 + 0.95, z1 - 2), Q(x1, y0 + 0.25, z1 - 2)]))
    tall = tallest(a)
    if tall:
        x0, y0, x1, y1, z0, h = tall
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        bot, tip = Q(cx, cy, z0 + h), Q(cx, cy, z0 + h + 11)
        a.add(line("edge", bot, tip))
        a.add(f'<circle class="wine" cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="1.1"/>')
        a.note(tip)


def skyline(parts, theme, rng, kind):
    """A row of towers behind the plate's two back edges, sunk below the plate."""
    c = CITY[theme]
    spots = []
    for row, depth in ((0, -3.2), (1, -1.7)):
        step = 1.35 if row else 1.7
        t = 0.2 + rng.random() * 0.4
        while t < G - 1.5:
            spots.append((t, depth, row))
            spots.append((depth, t, row))
            t += step + rng.random() * 0.5
    spots.sort(key=lambda s: (s[2], s[0] + s[1]))
    colors = [c["window"], c["trim"], c["extra"]] if kind == "cyber" else [c["window"]]
    for gx, gy, row in spots:
        w = 0.8 + rng.random() * 0.5
        d = 0.8 + rng.random() * 0.5
        x0, y0, x1, y1 = gx, gy, gx + w, gy + d
        room = TOP + (x0 + y0) * 5 - 4
        h = min(room + 22, (40 if row else 55) + rng.random() * 30)
        if h < 26:
            continue
        z0 = -22
        iso_box(parts, P, x0, y0, x1, y1, z0, h)
        z1 = z0 + h
        frac = 0.32 if kind == "cyber" else 0.14
        face_dots(parts, P, "left", x0, x1, y1, 0, z1 - 2, rng, frac, colors, 0.55 if row == 0 else 0.75)
        face_dots(parts, P, "right", y0, y1, x1, 0, z1 - 2, rng, frac * 0.7, colors, 0.45 if row == 0 else 0.6)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        roll = rng.random()
        if kind == "cyber":
            if roll < 0.45:
                a, b = P(cx, cy, z1), P(cx, cy, z1 + 8 + rng.random() * 6)
                parts.append(line("edge", a, b))
                parts.append(f'<circle cx="{b[0]:.1f}" cy="{b[1]:.1f}" r=".8" style="fill:{c["extra"]};stroke:none"/>')
            if roll > 0.6:
                parts.append(path("neon" if roll > 0.8 else "neon2", "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in (P(x0, y1, z1), P(x1, y1, z1), P(x1, y0, z1)))))
            if 0.3 < roll < 0.5 and row:
                parts.append(poly("holo", [P(x1, y0 + 0.15, z1 - 12), P(x1, y1 - 0.15, z1 - 12), P(x1, y1 - 0.15, z1 - 5), P(x1, y0 + 0.15, z1 - 5)]))
        else:  # noir: spires and stepped tops
            if roll < 0.4:
                apex = P(cx, cy, z1 + 10 + rng.random() * 10)
                parts.append(poly("sil", [P(x0, y1, z1), P(x1, y1, z1), apex]))
                parts.append(poly("silside", [P(x1, y0, z1), P(x1, y1, z1), apex]))
            elif roll < 0.75:
                iso_box(parts, P, x0 + w * 0.2, y0 + d * 0.2, x1 - w * 0.2, y1 - d * 0.2, z1, 6)
                apex = P(cx, cy, z1 + 6 + 7)
                parts.append(line("edge", P(cx, cy, z1 + 6), apex))


def cyber_back(parts, theme):
    skyline(parts, theme, random.Random("cyber-skyline"), "cyber")


def cyber_front(parts, theme):
    c = CITY[theme]
    # neon edging around every lot and a holo ad on a pole at the front corner
    for i in range(3):
        for j in range(3):
            x0, y0 = lot_origin(i, j)
            parts.append(path("neon2", "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in (P(x0, y0 + B), P(x0 + B, y0 + B), P(x0 + B, y0))), "stroke-width:.5;stroke-opacity:.6"))
    x, y = P(G - 0.25, G - 0.25)
    parts.append(line("edge", (x, y), (x, y - 14)))
    parts.append(f'<rect class="holo" x="{x - 7:.1f}" y="{y - 22:.1f}" width="14" height="8"/>')
    parts.append(line("neon", (x - 5, y - 19), (x + 5, y - 19)))
    parts.append(line("neon2", (x - 5, y - 16.5), (x + 2, y - 16.5)))


def cyber_tower(a: Art, theme: str, h: float, seed: str):
    rng = random.Random(seed)
    a.box(0.7, 0.7, 2.3, 2.3, 0, h, top="roof", left="wall", right="shade")
    colors = [CITY[theme]["window"], CITY[theme]["trim"], CITY[theme]["extra"]]
    face_dots(a.parts, Q, "left", 0.7, 2.3, 2.3, 2, h - 2, rng, 0.45, colors, 0.9)
    face_dots(a.parts, Q, "right", 0.7, 2.3, 2.3, 2, h - 2, rng, 0.3, colors, 0.7)
    cyber_building(a, "tower")


def cyber_empty_tower(a: Art, theme: str):
    cyber_tower(a, theme, 44, "tower-a")


def cyber_empty_pair(a: Art, theme: str):
    rng = random.Random("pair")
    colors = [CITY[theme]["window"], CITY[theme]["trim"]]
    a.box(0.4, 0.4, 1.4, 1.4, 0, 30)
    face_dots(a.parts, Q, "left", 0.4, 1.4, 1.4, 2, 28, rng, 0.45, colors, 0.9)
    face_dots(a.parts, Q, "right", 0.4, 1.4, 1.4, 2, 28, rng, 0.3, colors, 0.7)
    a.box(1.6, 1.5, 2.6, 2.6, 0, 18)
    face_dots(a.parts, Q, "left", 1.6, 2.6, 2.6, 2, 16, rng, 0.45, colors, 0.9)
    face_dots(a.parts, Q, "right", 1.5, 2.6, 2.6, 2, 16, rng, 0.3, colors, 0.7)
    cyber_building(a, "pair")


def cyber_empty_plaza(a: Art, theme: str):
    a.add(poly("lot", [Q(0.3, 0.3), Q(2.7, 0.3), Q(2.7, 2.7), Q(0.3, 2.7)]))
    x, y = Q(1.5, 1.5)
    a.add(f'<ellipse class="neon2" cx="{x:.1f}" cy="{y:.1f}" rx="13" ry="6.5"/>')
    a.add(f'<ellipse class="neon" cx="{x:.1f}" cy="{y:.1f}" rx="8" ry="4"/>')
    a.add(f'<path class="holo" d="M{x - 5:.1f} {y:.1f}L{x - 2:.1f} {y - 16:.1f}L{x + 2:.1f} {y - 16:.1f}L{x + 5:.1f} {y:.1f}Z" style="fill-opacity:.22"/>')
    a.add(f'<circle class="wine" cx="{x:.1f}" cy="{y - 18:.1f}" r="2.4"/>')
    a.note((x, y - 22))
    a.box(2.0, 0.5, 2.5, 0.9, 0, 6, top="winc")


# ---------- noir ----------

def noir_building(a: Art, building: str):
    for x0, y0, x1, y1, z0, h in list(a.boxes):
        if h < 8:
            continue
        z1 = z0 + h
        e = 0.06
        a.add(poly("metal", [Q(x0 - e, y1 + e, z1 - 2), Q(x1 + e, y1 + e, z1 - 2), Q(x1 + e, y1 + e, z1), Q(x0 - e, y1 + e, z1)]))
        a.add(poly("metalshade", [Q(x1 + e, y0 - e, z1 - 2), Q(x1 + e, y1 + e, z1 - 2), Q(x1 + e, y1 + e, z1), Q(x1 + e, y0 - e, z1)]))
    big = biggest(a)
    if big:
        x0, y0, x1, y1, z0, h = big
        z1 = z0 + h
        if h >= 10:  # a fire escape down the left face
            fx0, fx1 = x1 - 0.75, x1 - 0.2
            yy = y1 + 0.08
            z = z0 + 4
            k = 0
            while z < z1 - 3:
                a.add(line("fire", Q(fx0, yy, z), Q(fx1, yy, z)))
                a.add(line("fire", Q(fx1 if k % 2 else fx0, yy, z), Q(fx0 if k % 2 else fx1, yy, z + 4)))
                z += 4
                k += 1
        if building not in {"tank", "refinery"}:
            rooftop_tank(a, x0 + 0.4, y0 + 0.35, z1)


def noir_back(parts, theme):
    rng = random.Random("noir-skyline")
    # moon and halo, then two searchlight beams sweeping up
    parts.append('<circle cx="34" cy="20" r="15" style="fill:#efe8d0;fill-opacity:.08;stroke:none"/>')
    parts.append('<circle cx="34" cy="20" r="8.5" style="fill:#e6dfc6;stroke:none"/>')
    parts.append('<circle cx="31" cy="18" r="1.6" style="fill:#cfc8ae;stroke:none"/><circle cx="37" cy="23" r="1.1" style="fill:#cfc8ae;stroke:none"/>')
    parts.append(poly("beam", [(150, 70), (156, 70), (210, 0), (186, 0)]))
    parts.append(poly("beam", [(92, 74), (97, 74), (62, 0), (44, 0)]))
    skyline(parts, theme, rng, "noir")


def noir_front(parts, theme):
    c = CITY[theme]
    # wet streets: lamp light pooled and streaked on the roads
    for k1 in (1, 2):
        for k2 in (1, 2):
            a = M + k1 * B + (k1 - 1) * R + 0.3
            b = M + k2 * B + (k2 - 1) * R + 0.3
            x, y = P(a, b)
            parts.append(f'<ellipse cx="{x:.1f}" cy="{y + 1:.1f}" rx="6" ry="2.6" style="fill:{c["window"]};fill-opacity:.12;stroke:none"/>')
            parts.append(line("x", (x - 1, y + 1), (x - 1, y + 5)).replace('class="x"', f'style="stroke:{c["window"]};stroke-opacity:.35;stroke-width:.8"'))
    # fog low over the front edges
    parts.append(poly("fog", [P(0, G, 3), P(G, G, 3), P(G, G, -10), P(0, G, -10)]))
    parts.append(poly("fog", [P(G, 0, 3), P(G, G, 3), P(G, G, -10), P(G, 0, -10)]))


def noir_tenement(a: Art, theme: str):
    rng = random.Random("tenement")
    a.box(0.4, 0.6, 2.6, 2.6, 0, 26)
    face_dots(a.parts, Q, "left", 0.4, 2.6, 2.6, 2, 24, rng, 0.35, [CITY[theme]["window"]], 0.9)
    face_dots(a.parts, Q, "right", 0.6, 2.6, 2.6, 2, 24, rng, 0.25, [CITY[theme]["window"]], 0.7)
    a.door("left", 1.3, 1.7, 2.6, 5)
    noir_building(a, "tenement")


def noir_church(a: Art, theme: str):
    a.box(0.9, 0.4, 1.7, 1.2, 0, 30)
    a.windows("left", 0.9, 1.7, 1.2, 18, 27, 1, 1)
    pyramid(a, 0.9, 0.4, 1.7, 1.2, 30, 18)
    a.box(0.5, 1.2, 2.5, 2.6, 0, 15)
    a.gable(0.5, 1.2, 2.5, 2.6, 15, 8)
    x, y = Q(1.5, 2.6, 8)
    a.add(f'<circle class="win" cx="{x:.1f}" cy="{y:.1f}" r="2.6"/>')
    a.add(f'<circle class="windim" cx="{x:.1f}" cy="{y:.1f}" r="1.1"/>')
    a.door("left", 2.0, 2.3, 2.6, 6)


def noir_park(a: Art, theme: str):
    grass_patch(a, 0.3, 0.3, 2.7, 2.7)
    for gx, gy, s in sorted(((0.7, 0.8, 1.1), (2.2, 0.7, 0.9), (0.8, 2.2, 1.0), (2.1, 2.1, 0.8)), key=lambda t: t[0] + t[1]):
        x, y = Q(gx, gy)
        h = 11 * s
        a.add(path("trunk", f"M{x:.1f} {y:.1f}V{y - h:.1f}M{x:.1f} {y - h * 0.55:.1f}l-3 -3M{x:.1f} {y - h * 0.7:.1f}l3 -3.5M{x:.1f} {y - h:.1f}l-2 -2.5", "fill:none;stroke-width:.9"))
        a.note((x, y - h - 3))
    a.box(1.3, 1.6, 1.9, 1.75, 1.5, 1.2, top="roof", left="door", right="door")
    x, y = Q(1.6, 1.0)
    a.add(line("edge", (x, y), (x, y - 10)))
    a.add(f'<circle cx="{x:.1f}" cy="{y - 10.5:.1f}" r="1.3" style="fill:{CITY[theme]["window"]};stroke:none"/>')


# ---------- deepsea ----------

def deepsea_building(a: Art, building: str):
    cx, cy = Q(1.5, 1.5)
    rx, ry = 27, 13.5
    hd = max(24, min(40, cy - a.top - 2))
    a.add(path("glass", f"M{cx - rx:.1f} {cy:.1f}A{rx} {hd:.1f} 0 0 1 {cx + rx:.1f} {cy:.1f}A{rx} {ry} 0 0 1 {cx - rx:.1f} {cy:.1f}Z"))
    a.add(path("glassline", f"M{cx - rx * 0.72:.1f} {cy - hd * 0.45:.1f}A{rx * 0.8:.1f} {hd * 0.85:.1f} 0 0 1 {cx - rx * 0.2:.1f} {cy - hd * 0.93:.1f}"))
    a.add(path("ring", f"M{cx - rx:.1f} {cy:.1f}A{rx} {ry} 0 0 0 {cx + rx:.1f} {cy:.1f}"))
    for k in (-0.5, 0.5):
        a.add(path("glass", f"M{cx + rx * k:.1f} {cy + ry * 0.86:.1f}Q{cx + rx * k * 1.05:.1f} {cy - hd * 0.6:.1f} {cx:.1f} {cy - hd:.1f}", "fill:none;stroke-opacity:.35"))
    a.note((cx, cy - hd))


def deepsea_back(parts, theme):
    for x0, w in ((26, 12), (96, 16), (170, 13)):
        parts.append(poly("shaft", [(x0, 0), (x0 + w, 0), (x0 + w + 34, 150), (x0 + 12, 150)]))


def deepsea_front(parts, theme):
    c = CITY[theme]
    rng = random.Random("seabed")
    # glass tubes along every road
    for k in (1, 2):
        mid = M + k * B + (k - 1) * R + R / 2
        for along in ("x", "y"):
            if along == "x":
                f = lambda t, o, z: P(t, mid + o, z)  # noqa: E731
            else:
                f = lambda t, o, z: P(mid + o, t, z)  # noqa: E731
            r = 0.3
            parts.append(poly("glass", [f(0.1, -r, 4), f(G - 0.1, -r, 4), f(G - 0.1, r, 4), f(0.1, r, 4)]))
            parts.append(poly("glass", [f(0.1, r, 0), f(G - 0.1, r, 0), f(G - 0.1, r, 4), f(0.1, r, 4)]))
            parts.append(line("glassline", f(0.2, -0.05, 4), f(G - 0.2, -0.05, 4)))
            t = 0.8
            while t < G - 0.5:
                parts.append(line("ring", f(t, r, 0), f(t, r, 4)))
                t += 1.6
    for k1 in (1, 2):
        for k2 in (1, 2):
            a = M + k1 * B + (k1 - 1) * R + R / 2
            b = M + k2 * B + (k2 - 1) * R + R / 2
            x, y = P(a, b, 4)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" style="fill:{c["trim"]};fill-opacity:.15;stroke:none"/>')
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" style="fill:{c["trim"]};stroke:none"/>')
    # rocks and kelp on the margins
    for gx, gy in ((0.25, 1.6), (0.25, 6.2), (0.25, 10.4), (1.6, 0.25), (6.3, 0.25), (10.4, 0.25), (11.75, 3.3), (3.3, 11.75), (11.75, 9.6), (9.6, 11.75)):
        x, y = P(gx, gy)
        if rng.random() < 0.5:
            parts.append(f'<ellipse class="rock" cx="{x:.1f}" cy="{y - 1:.1f}" rx="{2 + rng.random() * 1.5:.1f}" ry="1.6"/>')
        else:
            h = 6 + rng.random() * 6
            parts.append(path("accent", f"M{x:.1f} {y:.1f}q-2 {-h * 0.5:.1f} 0 {-h:.1f}q2 {-h * 0.4:.1f} 0 {-h * 0.8:.1f}", f"stroke:{c['tree2']}"))


def coral(a: Art, theme: str, gx, gy, color, size=1.0):
    x, y = Q(gx, gy)
    h = 8 * size
    a.add(path("accent", f"M{x:.1f} {y:.1f}V{y - h:.1f}M{x:.1f} {y - h * 0.45:.1f}l-3 -3.5M{x:.1f} {y - h * 0.6:.1f}l3 -4M{x - 3:.1f} {y - h * 0.45 - 3.5:.1f}v-2", f"stroke:{color};stroke-width:1.2"))
    a.note((x, y - h - 4))


def deepsea_reef(a: Art, theme: str):
    c = CITY[theme]
    spots = [(0.7, 0.7), (1.8, 0.6), (2.4, 1.4), (0.8, 1.8), (1.6, 2.3), (2.4, 2.4), (1.4, 1.4)]
    for k, (gx, gy) in enumerate(sorted(spots, key=lambda t: t[0] + t[1])):
        if k % 3 == 1:
            x, y = Q(gx, gy)
            a.add(f'<ellipse cx="{x:.1f}" cy="{y - 2:.1f}" rx="4" ry="2.8" style="fill:#e8823a;stroke:{c["outline"]};stroke-width:.5"/>')
            a.add(path("hi", f"M{x - 2.5:.1f} {y - 2:.1f}q1.2 -1.5 2.5 0q1.2 1.5 2.5 0", "stroke:#ffb27a"))
        else:
            coral(a, theme, gx, gy, c["tree"] if k % 2 else c["tree2"], 0.8 + (k % 3) * 0.2)


def deepsea_pods(a: Art, theme: str):
    for gx, gy, r in ((0.9, 0.9, 9), (2.1, 1.2, 7), (1.3, 2.1, 8)):
        x, y = Q(gx, gy)
        a.cylinder(gx, gy, 0.14, 0, 5)
        a.add(path("glass", f"M{x - r:.1f} {y:.1f}A{r} {r * 1.1:.1f} 0 0 1 {x + r:.1f} {y:.1f}A{r} {r / 2:.1f} 0 0 1 {x - r:.1f} {y:.1f}Z"))
        a.add(path("ring", f"M{x - r:.1f} {y:.1f}A{r} {r / 2:.1f} 0 0 0 {x + r:.1f} {y:.1f}"))
        a.note((x, y - r * 1.1))


def deepsea_kelp(a: Art, theme: str):
    rng = random.Random("kelp")
    for gx, gy in sorted(((0.5 + rng.random() * 2, 0.5 + rng.random() * 2) for _ in range(11)), key=lambda t: t[0] + t[1]):
        lot_kelp = 0.8 + rng.random() * 0.7
        trees(a, theme, [(gx, gy, rng.randrange(2), lot_kelp)])
    for gx, gy in ((0.6, 2.4), (2.4, 0.6)):
        x, y = Q(gx, gy)
        a.add(f'<ellipse class="rock" cx="{x:.1f}" cy="{y - 1:.1f}" rx="3.2" ry="1.8"/>')


# ---------- garden (farmland) ----------

def garden_building(a: Art, building: str):
    for x0, y0, x1, y1, z0, h in list(a.boxes):
        if h < 8:
            continue
        z1 = z0 + h
        t = x0 + 0.25
        while t < x1 - 0.1:
            a.add(line("plank", Q(t, y1, z0), Q(t, y1, z1)))
            t += 0.3
        t = y0 + 0.25
        while t < y1 - 0.1:
            a.add(line("plank", Q(x1, t, z0), Q(x1, t, z1)))
            t += 0.3
    big = biggest(a)
    if big:  # a white X barn door on the right face
        x0, y0, x1, y1, z0, h = big
        a0, a1 = (y0 + y1) / 2 - 0.3, (y0 + y1) / 2 + 0.3
        dh = min(9, h - 2)
        a.add(poly("door", [Q(x1, a0, z0), Q(x1, a1, z0), Q(x1, a1, dh), Q(x1, a0, dh)]))
        a.add(line("trimline", Q(x1, a0, z0), Q(x1, a1, dh)))
        a.add(line("trimline", Q(x1, a1, z0), Q(x1, a0, dh)))
    if building == "mill":  # a windmill on the mill's front corner
        hub = Q(0.55, 2.6, 13)
        hx, hy = hub
        for dx, dy in ((10, -5), (-10, 5), (5, 10), (-5, -10)):
            ex, ey = hx + dx, hy + dy
            nx, ny = -dy * 0.18, dx * 0.18
            a.add(poly("hay", [(hx, hy), (ex, ey), (ex + nx, ey + ny), (hx + nx * 0.4, hy + ny * 0.4)], ' style="fill:#f4ecd8"'))
        a.add(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="1.4" style="fill:#7a5a3a;stroke:none"/>')
        a.note((hx, hy - 11))
    # hay bales by the front corner
    for gx, gy in ((2.75, 2.2), (2.75, 2.65)):
        x, y = Q(gx, gy)
        a.add(f'<ellipse class="hay" cx="{x:.1f}" cy="{y - 1.5:.1f}" rx="2.4" ry="1.8"/>')


def garden_front(parts, theme):
    # wheel ruts on the dirt roads and a wooden fence along the front edges
    for k in (1, 2):
        mid = M + k * B + (k - 1) * R + R / 2
        for off in (-0.2, 0.2):
            parts.append(line("rut", P(0.1, mid + off), P(G - 0.1, mid + off)))
            parts.append(line("rut", P(mid + off, 0.1), P(mid + off, G - 0.1)))
    for edge in ("left", "right"):
        f = (lambda t, z: P(t, G, z)) if edge == "left" else (lambda t, z: P(G, t, z))  # noqa: E731
        parts.append(line("rail", f(0, 2), f(G, 2)))
        parts.append(line("rail", f(0, 3.6), f(G, 3.6)))
        t = 0.0
        while t <= G + 0.01:
            parts.append(line("post", f(t, 0), f(t, 4.4)))
            t += 1.0
    x0, y0 = lot_origin(*PARK)
    for gx, gy in ((x0 + 2.4, y0 + 1.2), (x0 + 2.5, y0 + 1.6)):
        x, y = P(gx, gy)
        parts.append(f'<ellipse class="hay" cx="{x:.1f}" cy="{y - 1.5:.1f}" rx="2.4" ry="1.8"/>')


def soil(a: Art):
    a.add(poly("soil", [Q(0.3, 0.3), Q(2.7, 0.3), Q(2.7, 2.7), Q(0.3, 2.7)]))


def garden_wheat(a: Art, theme: str):
    soil(a)
    gy = 0.5
    while gy < 2.6:
        gx = 0.45
        while gx < 2.6:
            x, y = Q(gx, gy)
            a.add(line("wheat", (x, y), (x - 0.6, y - 4.5)))
            gx += 0.22
        gy += 0.34
    a.note(Q(0.45, 0.5, 5))


def garden_pumpkins(a: Art, theme: str):
    soil(a)
    rng = random.Random("pumpkins")
    for k in range(4):
        gy = 0.6 + k * 0.6
        a.add(path("vine", f"M{Q(0.4, gy)[0]:.1f} {Q(0.4, gy)[1]:.1f}L{Q(2.6, gy)[0]:.1f} {Q(2.6, gy)[1]:.1f}"))
        for gx in (0.6 + rng.random() * 0.3, 1.4 + rng.random() * 0.3, 2.2 + rng.random() * 0.2):
            x, y = Q(gx, gy)
            a.add(f'<ellipse class="pumpkin" cx="{x:.1f}" cy="{y - 1.5:.1f}" rx="2.3" ry="1.7"/>')
            a.add(line("vine", (x, y - 3), (x + 0.6, y - 4.2)))


def garden_veg(a: Art, theme: str):
    soil(a)
    for k in range(5):
        gx = 0.5 + k * 0.48
        a.add(path("vine", f"M{Q(gx, 0.4)[0]:.1f} {Q(gx, 0.4)[1]:.1f}L{Q(gx, 2.0)[0]:.1f} {Q(gx, 2.0)[1]:.1f}", "stroke-width:1.6;stroke:#7fb85a"))
    for gx, gy in ((0.8, 2.4), (1.4, 2.45), (2.0, 2.4), (1.1, 2.25)):
        x, y = Q(gx, gy)
        a.add(f'<ellipse class="hay" cx="{x:.1f}" cy="{y - 1.8:.1f}" rx="2.6" ry="2"/>')


def garden_plot(a: Art, theme: str):
    empty_plot(a, theme)
    x, y = Q(1.0, 1.3)  # a scarecrow
    a.add(line("post", (x, y), (x, y - 13)))
    a.add(line("post", (x - 4, y - 9), (x + 4, y - 9)))
    a.add(f'<circle class="hay" cx="{x:.1f}" cy="{y - 14:.1f}" r="2"/>')
    a.add(poly("roof", [(x - 3, y - 15.5), (x + 3, y - 15.5), (x, y - 18.5)]))
    a.note((x, y - 19))


# ---------- registry ----------

BUILDING = {
    "cyber": cyber_building,
    "noir": noir_building,
    "deepsea": deepsea_building,
    "garden": garden_building,
}
PLATE_BACK = {"cyber": cyber_back, "noir": noir_back, "deepsea": deepsea_back}
PLATE_FRONT = {"cyber": cyber_front, "noir": noir_front, "deepsea": deepsea_front, "garden": garden_front}
NO_LANES = {"deepsea", "garden"}
EMPTY = {
    "cyber": [cyber_empty_tower, empty_plot, cyber_empty_plaza, cyber_empty_pair],
    "noir": [noir_tenement, empty_plot, noir_park, noir_church],
    "deepsea": [deepsea_reef, empty_plot, deepsea_pods, deepsea_kelp],
    "garden": [garden_wheat, garden_plot, garden_pumpkins, garden_veg],
}
