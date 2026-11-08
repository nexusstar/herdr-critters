"""Generate a theme's art (sprites, scenes, icons) as SVG, or as PNG for a raster theme.

The engine is theme-agnostic. A theme is a Python package art/themes/<id>/ that
exports these names (see art/themes/retro):
  SPRITES, POSES, BATCHES  sprite grids, their per-status pose data, and the extra sprite batches
  POSE_COLORS              palette entries added to every sprite for pose marks
  BLOCKED_EYE              palette key used to draw the eyes of the "blocked" status
  BANG, SWEAT, CHECK, BOLT small glyph grids placed next to a sprite by status
  SCENES, ICONS            full pictures, each as (palette, rows)
Each picture is an ASCII grid: one character
per pixel, "." is transparent. Output goes to mods/herdr-critters/themes/<id>/art/.

A vector theme (see art/themes/edo) sets VECTOR = True and draws its own SVG text:
  SPRITES                  name -> a function of the status that gives the sprite's SVG
  BATCHES                  the sprite batches, each with its own SPRITES
  SCENES, ICONS            name -> SVG text
It needs none of the grid names.

A raster theme sets RASTER = True and draws PNG files with any engine it likes:
  SPRITES                  name -> a function of the status that gives the sprite's PNG bytes
  BATCHES                  the sprite batches, each with its own SPRITES
  SCENES, ICONS            name -> PNG bytes
Its files end in .png; set `artExt: "png"` in the theme's theme.js so the mod loads them.

Run from the repo root:
    uv run --no-project art/generate.py [--theme <id>]            (default: retro)
    uv run --no-project art/generate.py --theme <id> --batch <name> <dir>
The second form draws only that sprite batch into <dir>, leaving the mod's art alone.
A full theme run also writes its eight space-factory SVGs from
art/space_factory_art.py and the isometric city (plate, empty lot and one
building per factory type) from art/space_city_art.py, both SVG in every theme.
"""

import argparse
import importlib
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from art.space_city_art import generate as generate_city_art
from art.space_factory_art import generate as generate_space_art

STATUSES = ("idle", "working", "blocked", "done")


def load_theme(theme_id: str) -> ModuleType:
    return importlib.import_module(f"art.themes.{theme_id}")


def put(rows: list[str], x: int, y: int, text: str) -> None:
    rows[y] = rows[y][:x] + text + rows[y][x + len(text) :]


def place(rows: list[str], glyph: list[str], side: str) -> None:
    """Put a glyph in the highest free spot: on `side` one pixel clear of the sprite,
    else on the other side, else touching it."""
    for s, margin in ((side, 1), ("left" if side == "right" else "right", 1), (side, 0)):
        if place_at(rows, glyph, s, margin):
            return


def place_at(rows: list[str], glyph: list[str], side: str, margin: int) -> bool:
    h, w = len(rows), len(rows[0])
    gh, gw = len(glyph), len(glyph[0])
    xs = range(w - gw, -1, -1) if side == "right" else range(0, w - gw + 1)

    def free(x: int, y: int) -> bool:
        for gy, line in enumerate(glyph):
            for gx, ch in enumerate(line):
                if ch == ".":
                    continue
                for ny in range(y + gy - margin, y + gy + margin + 1):
                    for nx in range(x + gx - margin, x + gx + margin + 1):
                        if 0 <= ny < h and 0 <= nx < w and rows[ny][nx] != ".":
                            return False
        return True

    for y in range(0, h - gh + 1):
        for x in xs:
            if free(x, y):
                for gy, line in enumerate(glyph):
                    for gx, ch in enumerate(line):
                        if ch != ".":
                            put(rows, x + gx, y + gy, ch)
                return True
    return False


def pose(theme: ModuleType, name: str, status: str) -> tuple[dict[str, str], list[str]]:
    palette, base = theme.SPRITES[name]
    p = theme.POSES[name]
    rows = list(base)
    for x, y in p["eyes"]:
        if status == "idle":  # closed: a line where the eye's bottom was
            put(rows, x, y, p["face"])
            put(rows, x, y + 1, p["line"])
        elif status == "blocked":
            put(rows, x, y, theme.BLOCKED_EYE)
            put(rows, x, y + 1, theme.BLOCKED_EYE)
        elif status == "done":  # happy: only the top half, an upturned eye
            put(rows, x, y + 1, p["face"])
    for x, y, text in p[status]:
        put(rows, x, y, text)
    if status == "working":
        place(rows, theme.BOLT, "left")
    elif status == "blocked":
        place(rows, theme.BANG, "left")
        place(rows, theme.SWEAT, "right")
    elif status == "done":
        place(rows, theme.CHECK, "left")
    return {**palette, **theme.POSE_COLORS}, rows


def svg(palette: dict[str, str], rows: list[str]) -> str:
    w, h = len(rows[0]), len(rows)
    assert all(len(r) == w for r in rows), "ragged grid"
    rects: list[str] = []
    for y, row in enumerate(rows):
        x = 0
        while x < w:
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            run = x
            while run < w and row[run] == ch:
                run += 1
            rects.append(f'<rect x="{x}" y="{y}" width="{run - x}" height="1" fill="{palette[ch]}"/>')
            x = run
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 8}" height="{h * 8}" '
        f'shape-rendering="crispEdges">{"".join(rects)}</svg>\n'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--theme", default="retro", help="theme id, a package under art/themes/")
    parser.add_argument("--batch", nargs=2, metavar=("NAME", "DIR"), help="only that sprite batch, into DIR")
    args = parser.parse_args()
    try:
        theme = load_theme(args.theme)
    except ModuleNotFoundError as exc:
        if exc.name != f"art.themes.{args.theme}":
            raise
        parser.error(f"unknown theme: {args.theme}")
    names, out = list(theme.SPRITES), ROOT / "mods" / "herdr-critters" / "themes" / args.theme / "art"
    if args.batch:
        names = list(theme.BATCHES[args.batch[0]].SPRITES)
        out = Path(args.batch[1])
    out.mkdir(parents=True, exist_ok=True)
    for old in [*out.glob("sprite-*.svg"), *out.glob("sprite-*.png")]:
        old.unlink()
    raster = getattr(theme, "RASTER", False)
    if raster or getattr(theme, "VECTOR", False):  # the theme draws its own SVG text or PNG bytes
        sprites = {f"{name}-{status}": theme.SPRITES[name](status) for name in names for status in STATUSES}
        scenes, icons = theme.SCENES, theme.ICONS
    else:
        sprites = {f"{name}-{status}": svg(*pose(theme, name, status)) for name in names for status in STATUSES}
        scenes = {name: svg(*pic) for name, pic in theme.SCENES.items()}
        icons = {name: svg(*pic) for name, pic in theme.ICONS.items()}
    for group, items in (("sprite", sprites), ("scene", scenes), ("icon", icons)):
        for name, data in items.items():
            if raster:
                (out / f"{group}-{name}.png").write_bytes(data)
            else:
                (out / f"{group}-{name}.svg").write_text(data)
    print(f"wrote {len(sprites) + len(scenes) + len(icons)} files to {out}")
    if not args.batch:
        count = generate_space_art(args.theme, out)
        print(f"wrote {count} space factory icons to {out}")
        count = generate_city_art(args.theme, out)
        print(f"wrote {count} isometric city files to {out}")


if __name__ == "__main__":
    main()
