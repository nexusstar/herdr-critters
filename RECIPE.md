# Herdr critters

A Critters panel with compact summary cards for spaces and a themed critter
card for every agent. Each agent has its own sprite, standing in a scene that
changes with its status.

![Herdr critters](preview.png)

## What you see

The mod fills the layout's `agents` block:

- **Header** (38 px): a dither icon and theme button (shows the active theme,
  such as `RETRO`) at the left, and the total working-agent count at the right.
- **Spaces section**: a `SPACES` header with a chevron, total count and `+`
  button; it starts expanded and sits above the Agents section. Below it is one
  isometric city (240x192 px at a 268 px sidebar; it scales with the sidebar,
  0.6x to 1.6x): a plate of 3 x 3 blocks (12 x 12 grid units, 10/5 px per unit,
  2:1 isometric) with two roads each way, lane dashes, a park with a pond and
  trees in the middle block and eight lots around it. Each of the first eight
  spaces, in `spaces()` order, is a building on a lot, back to front. Empty
  lots take one of four looks by lot (`EMPTY_ORDER` in `main.js`, so
  neighbours differ): a grove of nine mixed trees, a fenced plot with three
  trees and a `+` sign, a park with a path, fountain and bench, and a 3 x 3
  orchard. `art/city_dress.py` gives four themes their own city on the same
  geometry: cyber (neon edges, wall signs, holo billboards and antennas; a dim
  tower skyline behind the plate; filler towers and a holo plaza on empty
  lots), noir (cornice ledges, fire escapes, rooftop water tanks; a skyline of
  spires under a moon with two searchlight beams, fog, lamp-lit wet streets;
  a tenement, a church and a bare park on empty lots), deepsea (a glass dome
  over each building, glass tubes along the roads, light shafts, rocks and
  kelp; a reef, pods and kelp on empty lots) and garden (red barns with
  planks and X doors, a windmill on the mill, hay bales, dirt roads with ruts,
  a fence; wheat, pumpkins, vegetable rows and a scarecrow plot on empty lots).
  A building is the
  space's factory type drawn as isometric boxes, gables and cylinders, in one
  of four wall/roof variants. On its roof stands a 7x5 flag in the space's
  saved color; the active space's flag pulses and a chevron bobs above its
  roof. A working space shows three soft smoke puffs (4-6 px, the theme's `sub`
  color, 10-45% opacity) bobbing above its chimney; a blocked space a 3 px
  light in the blocked color pulsing atop the flagpole, a done space the same
  light steady in the done color; idle shows nothing. Agents
  are not drawn in the city; they stay in the Agents section. Under the city a caption shows the hovered space, else the active
  one: color square, name (VT323 18 px), status box, then machine icon, branch
  or folder, tab and agent counts. Spaces past the eighth are 24 px rows (a
  16 px factory icon, name and status box).
- **Agents section**: an `AGENTS` header with the `BY MACHINE` / `BY SPACE`
  toggle. That toggle groups agents only. The existing themed agent cards,
  group headers and controls follow below it.
- **Agent cards**, 8 px apart, 10 px side padding, 2 px border and the scene's
  card color as fill. Left is a 74x62 sprite box; right is the name (VT323
  20 px) with a status box beside it, and the session name below.
- **Empty states**: `NO SPACES YET` when there are no spaces; `NO AGENTS` on an
  space's caption when it has no agents; `NO PLAYERS YET` and help text when the
  Agents section has no agents.
- **Narrow sidebar** (sidebar under 160 px wide): a combined compact rail shows
  factory icons and a create button above the existing 36x30 agent sprite boxes.

The palette is fixed per theme and does not follow the Herdr theme. Agent scenes
are local `dusk` (purple) or remote `den` (blue-gray), `dawn` (rust) and `moss`
(green) in turn. Space tiles and active-card accents use the saved colors from
the Spaces mod.

## How it behaves

- **Spaces**: the first eight `spaces()` entries are buildings, including
  spaces without agents and remote spaces, in Herdr's order (local first, then
  remote machines by name). Click a building to select its space; right-click
  opens Herdr's standard space menu (rename, close). Click an empty lot or the
  `+` to create a space. Hovering a building puts it in the caption.
  Reordering is not offered in the city. The Spaces section is expanded by
  default; its collapse state is shared under `herdr-critters.spaces-collapsed`.
- The caption's status box uses the active theme's word and color for the
  space's highest-priority status; it says `NO AGENTS` for a
  space with none.
- A space's factory type is assigned by space ID and stored in shared state
  (`herdr-critters.space-buildings`). It is stable across restarts, reordering
  and theme changes. Eight types are kept distinct while available; after
  that, new spaces reuse a type without changing existing assignments. The
  same type draws the flat icon in the narrow rail and the building in the city.
- **Names**: each agent gets a random name from a list of 30 (pixel, byte,
  nova, rook, ziggy, mochi, bolt, echo, juno, kiwi, luma, miso, nimbus, onyx,
  pepper, quill, rusty, sprout, tango, umbra, vega, waffle, yeti, zephyr, comet,
  dusty, fable, gizmo, hopper, ivory). The `edo` theme has its own 30 (onigiri,
  sushi, dango, mochi, ramen, tofu, taiyaki, matcha, gyoza, bento, tempura,
  wasabi, sake, udon, natto, yuzu, miso, senbei, anpan, tamago, kokeshi, daruma,
  chochin, geta, sensu, furin, kendama, torii, kasa, maneki). The pick uses `crypto` random, never two
  the same, and is kept in `localStorage` by agent address across restarts (key
  `names` for retro, `names.<id>` for other themes). Past 30 agents a name
  repeats with a number (`pixel 2`) and shares a sprite.
- **Status**, on the agent's status box, sprite, scene and corner badge:
  - idle: the theme's idle word, eyes shut, badge `z`/`Z` blinking.
  - working: the theme's working word, a yellow bolt, badge a 4-frame spinner,
    the sprite bobs 3 px.
  - blocked: the theme's blocked word, red eyes, a `!` and sweat drop, badge
    `!` pulsing, the card border red.
  - done: the theme's done word, happy eyes, a green check, badge `✓`.
- The focused agent's card has an orange `#e8922e` border.
- Click an agent card to focus its pane (`pane.focus`). Hover shows a pin
  button; it runs `terminal.pin`. Pinned agents go first in their group.
- Click an agent group header to collapse the group. The collapsed groups are
  shared state (`herdr-critters.collapsed`, keyed by `space:<id>` or
  `machine:<name>`). Hover also shows a minus button beside the pin; it makes
  the card compact, one line with a 36x30 sprite box, the name and status (a
  plus button opens it again). Compact cards are shared state
  (`herdr-critters.compact`, keyed by agent address).
- Right-click an agent card (or a small sprite box) for a menu: pin/unpin,
  collapse/expand the card, or collapse/show its group. The pointer popup is
  this same mod, with `props().menu` set to the agent's address.
- The fixed header keeps the dither icon and theme button at left and the total
  working-agent count at right. The `BY MACHINE` / `BY SPACE` toggle lives in the Agents header
  and affects only agent groups. The theme button is shared state
  (`herdr-critters.theme`; unknown or missing means `retro`).
- The agent list order is sent to Herdr with `setAgentOrder`.

## Built from

- **Layout** `layouts/critters.json`: the custom layout replaces the standalone
  Spaces block with `{ "mod": "herdr-critters" }` in its sidebar list, avoiding
  duplicate space navigation.
- **Mod** `mods/herdr-critters/`: `main.js` (one `View`, theme-agnostic),
  `mod.json` (`place: none`), `themes/` (registry `index.js` and one folder per
  theme with `theme.js` and `art/`), `icons/` (local laptop and remote network),
  and `fonts/`.
- **herdr functions**: `agents`, `terminals`, `spaces`, `machines`, `layout`,
  `theme`, `shared`, `setShared`, `setAgentOrder`, `run`, `openOverlay`,
  `closeOverlay`, `props`.
- **Commands**: `space.select`, `space.new`, `space.move`, `pane.focus`,
  `terminal.pin`.
- **Shipped mods it uses**: the standard `menu` for space management, plus the
  `pin`, `pin-off`, `plus`, `minus`,
  `chevron-down` and `chevron-right` icons of
  `workspace-chrome`.
- **Programs, network, files**: none. It does not run programs, reach the
  network or read files outside its own folder.
- **Art**: Theme assets in `mods/herdr-critters/themes/<id>/art/`: one sprite
  per agent name and status (`sprite-<name>-<status>`), a scene per status
  (`scene-<status>`), machine icons, and eight space-factory silhouettes
  (`space-<type>.svg`), and the isometric city: `city-plate.svg`,
  `city-empty-<0-3>.svg` and `city-<type>.svg`, from `art/space_city_art.py`, which
  also writes the geometry the mod reads (`mods/herdr-critters/city.js`). Factory icons are SVG in all themes and use the same
  underlying silhouettes with a theme-specific finish. They are generated by
  `uv run --no-project art/generate.py --theme <id>` (default `retro`), with the
  factory artwork defined in `art/space_factory_art.py`. Agent art is generated
  from `art/themes/<id>/`: ASCII grids for retro (pixel art), drawing code for
  edo (vector woodblock prints), y2k (glossy vector critters) and cyber (neon
  vector mascots). Raster agent themes draw their assets as PNG: noir (black
  cutout critters, drawn with skia-python; run generate.py with
  `--with pillow --with skia-python`), deepsea (soft gel critters, drawn with
  skia-python; also `--with imagequant`) and garden (felt craft critters,
  painted with Pillow and numpy; run generate.py with `--with numpy --with pillow`).
- **Fonts**: Silkscreen and VT323 (retro, noir, deepsea, garden), Shippori Mincho and Yuji Syuku cut
  to Latin letters (edo), Orbitron and Share Tech Mono (y2k, cyber), all SIL Open Font
  License, in `fonts/`.

## Themes

A theme is `themes/<id>/theme.js`, a default export of one object:

- `id`, `label` (shown on the header button), `art` (art folder path),
  `fonts` (`pixel`, `mono`, optional `monoSize` and `monoLine` for the name
  text, default 20 and `18px`), optional `namesKey` (storage key for names) and
  optional `artExt` (the art files' type, `"svg"` by default, `"png"` for
  raster art).
- `colors`: `bg`, `head`, `machine`, `focus`, `text`, `sub` and the rest the
  view uses (badge, borders, hover, dividers).
- `scenes` (each `card`, `edge`, `box`, `label`), `localScene` and
  `remoteScenes`.
- `status`: `working`, `blocked`, `done`, `idle`, each `{ word, color }`.
- `names`: the 30 agent names; each needs its sprites in `art/`.

`themes/index.js` exports `THEMES` (cycle order), `DEFAULT_THEME` (`retro`) and
`themeById(id)` (unknown id gives the default). To add a theme: write
`theme.js`, add the art, import it in `index.js` and add it to `THEMES`.
