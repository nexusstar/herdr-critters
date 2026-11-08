// Spaces as compact summary cards, agents as themed critters with a sprite,
// status badge and scene. Agent groups follow machine or space order.

import { View, div, image, svg } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { agents, terminals, spaces, machines, run, setAgentOrder, layout, shared, setShared, theme, openOverlay, closeOverlay, props } from "herdr";
import { webcrypto } from "crypto";
import { THEMES, themeById } from "./themes/index.js";
import CITY from "./city.js";

const THEME_KEY = "herdr-critters.theme";
const activeTheme = () => themeById(shared(THEME_KEY));

function find(node, id) {
  if (node?.id === id) return node;
  for (const child of node?.children ?? []) {
    const found = find(child, id);
    if (found) return found;
  }
  return null;
}

// The sidebar's rail goes by its width, as in the shipped agents mod.
const narrow = () => (find(layout(), "sidebar")?.size?.px ?? Infinity) < 160;

// An agent on another machine has a `machine/` address prefix.
const machineOf = (a) => (a.address.includes("/") ? a.address.split("/")[0] : null);

// A random item from the OS random source, so picks differ on every start.
const pickRandom = (arr) => arr[webcrypto.getRandomValues(new Uint32Array(1))[0] % arr.length];

const clean = (s) => (s ?? "").replace(/^[^\p{L}\p{N}]+/u, "").trim();

// The session's name: the terminal's core name, else the title the agent gives
// its terminal when that says more than the program's name or a folder.
function sessionName(a, terminal) {
  if (terminal?.name) return terminal.name;
  const live = clean(a.title);
  const generic = !live || live === a.program?.name || live.toLowerCase() === a.program?.key || /^[~/]|^[A-Za-z]:\\/.test(live) || live.includes("@");
  return generic ? null : live;
}

// The line under the name: "space -> session", else the space and its tab.
function detail(a, tabs, session) {
  if (session) return session;
  const tab = tabs.find((t) => t.id === a.tab);
  return tab?.named ? tab.name : tab ? `tab ${tab.name}` : a.program?.name ?? "";
}

// Cards go under their machine or under their space; the choice is shared state.
const GROUP_KEY = "herdr-critters.group";
const groupBy = () => (shared(GROUP_KEY) === "space" ? "space" : "machine");

// Collapsed groups ("space:<id>" / "machine:<name>") and compact cards (by address),
// each a shared map of id -> true.
const COLLAPSED_KEY = "herdr-critters.collapsed";
const COMPACT_KEY = "herdr-critters.compact";
const SPACES_COLLAPSED_KEY = "herdr-critters.spaces-collapsed";
const SPACE_BUILDINGS_KEY = "herdr-critters.space-buildings";
const SPACE_BUILDINGS = [
  "mill", "power", "tank", "warehouse", "foundry", "waterworks", "assembly", "refinery",
];
const SPACE_MARK_COLORS = {
  ansi6: "#22a99a",
  ansi3: "#e3814f",
  ansi4: "#5b8def",
  ansi5: "#8b7cf6",
  ansi2: "#3fae6a",
  ansi1: "#d9649a",
};
const isSet = (key, id) => Boolean(shared(key)?.[id]);

// Which empty-lot look each lot gets, so neighbours differ.
const EMPTY_ORDER = [0, 2, 3, 1, 3, 0, 1, 2];
function spaceBuildingHash(id) {
  let hash = 2166136261;
  for (const char of String(id)) hash = Math.imul(hash ^ char.charCodeAt(0), 16777619);
  return hash >>> 0;
}
function toggle(key, id) {
  const map = { ...(shared(key) ?? {}) };
  if (map[id]) delete map[id];
  else map[id] = true;
  setShared(key, map);
}

// The collapse id of the group an agent shows in.
const groupIdOf = (a) => (groupBy() === "space" ? `space:${a.space}` : `machine:${machineOf(a) ?? ""}`);

// Where a theme's picked names are stored. A theme can set `namesKey` to keep an old key
// (retro keeps "names" so current users keep their names).
const namesKey = (look) => look.namesKey ?? `names.${look.id}`;

// The art files' type: "svg" by default, "png" for a theme drawn as raster art.
const artExt = (look) => look.artExt ?? "svg";

export default class RetroAgents extends View {
  init() {
    this.hovered = null;
    this.look = null;
    this.picked = {};
    this.hoverSpace = null;
  }

  // The status entry for an agent's word; an unknown word reads as idle.
  statusOf(s) {
    return this.look.status[s] ?? this.look.status.idle;
  }

  pixel(el, size, color) {
    return el.font_family(this.look.fonts.pixel).text_size(size).text_color(color);
  }

  // Switch to the active theme; each theme keeps its own picked names, kept across
  // restarts so a name doesn't change under you.
  useTheme(look) {
    if (this.look?.id === look.id) return;
    this.look = look;
    this.picked = JSON.parse(localStorage.getItem(namesKey(look)) ?? "{}");
  }

  // One name from the theme's names per agent, never two the same: an agent keeps its picked
  // name while no earlier agent holds it, else gets a random free one.
  names(list) {
    const out = new Map();
    const taken = new Set();
    const NAMES = this.look.names;
    let dirty = false;
    for (const a of list) {
      let name = this.picked[a.address];
      if (!name || !NAMES.includes(name) || taken.has(name)) {
        const free = NAMES.filter((n) => !taken.has(n));
        name = pickRandom(free.length ? free : NAMES);
        this.picked[a.address] = name;
        dirty = true;
      }
      // Only past 30 agents: the same name again, with a number.
      let unique = name;
      for (let n = 2; taken.has(unique); n++) unique = `${name} ${n}`;
      taken.add(unique);
      out.set(a.address, unique);
    }
    if (dirty) localStorage.setItem(namesKey(this.look), JSON.stringify(this.picked));
    return out;
  }

  // The sprite box: scene, sprite, and the corner badge that tells the state at a glance.
  // `name` is the agent's picked name: each name has its own sprite.
  stage(a, scene, w, h, name) {
    const { art, colors: C, status: STATUS } = this.look;
    const ext = artExt(this.look);
    const st = a.status;
    const spriteW = Math.round(w * 0.66);
    const spriteH = Math.round(spriteW * 0.8);
    const left = Math.round((w - spriteW) / 2);
    // Feet on the bricks: the scene's ground is its bottom 7 of 30 rows.
    const top = h - Math.round(h * (7 / 30)) - spriteH + 2;
    const sprite = image(`${art}/sprite-${name}-${STATUS[st] ? st : "idle"}.${ext}`).absolute().left(left).top(top).w(spriteW).h(spriteH);
    const badge = div()
      .absolute()
      .top(3)
      .right(3)
      .size(Math.max(12, Math.round(w * 0.2)))
      .flex()
      .items_center()
      .justify_center()
      .bg(C.badgeBg)
      .border(1)
      .border_color(st === "idle" ? C.idleEdge : this.statusOf(st).color);
    const mark = () => this.statusMark(st);
    return div()
      .relative()
      .w(w)
      .h(h)
      .flex_none()
      .overflow_hidden()
      .border(2)
      .border_color(st === "idle" ? scene.box : this.statusOf(st).color + C.statusEdgeAlpha)
      .child(image(`${art}/scene-${STATUS[st] ? st : "idle"}.${ext}`).absolute().left(0).top(0).w(w - 4).h(h - 4))
      .child(st === "working" ? sprite.loop("top", { from: top, to: top - 3, period: 520 }) : sprite)
      .child(badge.child(mark()));
  }

  // The corner-badge mark for a status: z, a spinner, a pulsing !, a check.
  statusMark(st) {
    const { colors: C, status: STATUS } = this.look;
    return ({
      idle: () => this.pixel(div(), 9, C.idleMark).frames(["z", "z", "Z", "Z"], 450),
      working: () => this.pixel(div(), 9, STATUS.working.color).frames(["▘", "▝", "▗", "▖"], 140),
      blocked: () => this.pixel(div(), 10, STATUS.blocked.color).child("!").loop("opacity", { from: 0.25, to: 1, period: 700 }),
      done: () => div().text_size(10).font_bold().text_color(STATUS.done.color).child("✓"),
    }[st] ?? (() => div()))();
  }

  // A small icon button on a card; a click does `act` and not the card's own click.
  cardButton(id, tooltip, icon, act) {
    const C = this.look.colors;
    return div()
      .id(id)
      .flex_none()
      .p(2)
      .text_color(C.sub)
      .cursor_pointer()
      .hover((el) => el.text_color(C.text))
      .tooltip(tooltip)
      .on_click((_e, cx) => {
        cx.stop_propagation();
        act();
        this.hovered = null;
        cx.notify();
      })
      .child(svg(`mods/workspace-chrome/${icon}.svg`).size(12));
  }

  // The status word in its box.
  statusBox(a) {
    const s = this.statusOf(a.status);
    return this.pixel(div(), 10, s.color)
      .flex_none()
      .mt(-1)
      .px(5)
      .h(17)
      .flex()
      .items_center()
      .border(1)
      .border_color(a.status === "idle" ? this.look.colors.idleBox : s.color)
      .child(s.word);
  }

  // The card's frame: hover, click to focus, and the edge color.
  cardFrame(a, scene) {
    const { colors: C, status: STATUS } = this.look;
    const edge = a.focused ? C.focus : a.status === "blocked" ? STATUS.blocked.color : scene.edge;
    return h_flex()
      .id(`card-${a.address}`)
      .relative()
      .flex_none()
      .items_center()
      .bg(scene.card)
      .border(2)
      .border_color(edge)
      .cursor_pointer()
      .hover((el) => el.bg(scene.edge))
      .on_hover((on, cx) => {
        if (on) this.hovered = a.address;
        else if (this.hovered === a.address) this.hovered = null;
        cx.notify();
      })
      .on_click(() => run("pane.focus", { pane: a.pane }))
      .on_mouse_down("right", (_e, cx) => this.openMenu(a, cx));
  }

  // Right-click: a popup at the pointer, drawn by this mod with `props().menu`.
  openMenu(a, cx) {
    cx.stop_propagation();
    this.hovered = null;
    openOverlay({ mod: "herdr-critters", kind: "popup", frame: "none", width: 190, height: 92, props: { menu: a.address } });
  }

  // The context menu: pin, card collapse and group collapse for one agent.
  menu(address) {
    const { colors: C } = this.look;
    const a = agents().find((x) => x.address === address);
    const close = () => closeOverlay(props().overlay);
    if (!a) {
      close();
      return div();
    }
    const group = groupIdOf(a);
    const item = (id, label, act) => this.pixel(h_flex(), 10, C.sub)
      .id(`menu-${id}`)
      .h(26)
      .px(8)
      .items_center()
      .cursor_pointer()
      .hover((el) => el.bg(C.divider).text_color(C.text))
      .on_click(() => {
        act();
        close();
      })
      .child(label);
    return v_flex()
      .size_full()
      .p(4)
      .bg(C.bg)
      .border(2)
      .border_color(C.btnEdge)
      .child(item("pin", a.pinned ? "UNPIN" : "PIN TO TOP", () => run("terminal.pin", { terminal: a.address, pinned: !a.pinned })))
      .child(item("card", isSet(COMPACT_KEY, a.address) ? "EXPAND CARD" : "COLLAPSE CARD", () => toggle(COMPACT_KEY, a.address)))
      .child(item("group", isSet(COLLAPSED_KEY, group) ? "SHOW GROUP" : "COLLAPSE GROUP", () => toggle(COLLAPSED_KEY, group)));
  }

  pinButton(a) {
    return this.cardButton(`pin-${a.address}`, a.pinned ? "Unpin" : "Pin to the top", a.pinned ? "pin-off" : "pin",
      () => run("terminal.pin", { terminal: a.address, pinned: !a.pinned }));
  }

  compactButton(a, compact) {
    return this.cardButton(`compact-${a.address}`, compact ? "Expand the card" : "Collapse the card", compact ? "plus" : "minus",
      () => toggle(COMPACT_KEY, a.address));
  }

  // A collapsed card: one thin line with a small sprite, the name and the status.
  compactCard(a, scene, name) {
    const { colors: C, fonts } = this.look;
    const hot = this.hovered === a.address;
    return this.cardFrame(a, scene)
      .p(3)
      .gap(8)
      .child(this.stage(a, scene, 36, 30, this.picked[a.address]))
      .child(div().flex_1().min_w(0).font_family(fonts.mono).text_size(fonts.monoSize ?? 20).line_height(fonts.monoLine ?? "18px").text_color(C.text).truncate().child(name))
      .when(hot, (el) => el.child(this.compactButton(a, true)))
      .when(hot || a.pinned, (el) => el.child(this.pinButton(a)))
      .child(this.statusBox(a).mt(0).mr(2));
  }

  card(a, scene, tabs, name, session) {
    if (isSet(COMPACT_KEY, a.address)) return this.compactCard(a, scene, name);
    const { colors: C, fonts } = this.look;
    const hot = this.hovered === a.address;
    return this.cardFrame(a, scene)
      .p(6)
      .gap(10)
      .child(this.stage(a, scene, 74, 62, this.picked[a.address]))
      .child(
        v_flex()
          .flex_1()
          .min_w(0)
          .gap(5)
          .child(
            h_flex()
              .gap(6)
              .items_center()
              .child(div().flex_1().min_w(0).font_family(fonts.mono).text_size(fonts.monoSize ?? 20).line_height(fonts.monoLine ?? "18px").text_color(C.text).truncate().child(name))
              .child(this.statusBox(a)),
          )
          .child(div().text_size(11.5).text_color(C.sub).truncate().child(detail(a, tabs, session))),
      )
      .child(h_flex().absolute().bottom(4).right(4)
        .when(hot, (el) => el.child(this.compactButton(a, false)))
        .when(hot || a.pinned, (el) => el.child(this.pinButton(a))));
  }

  // A small outlined button in the top bar.
  headerButton(id, tooltip, onClick, label) {
    const C = this.look.colors;
    return this.pixel(div(), 9, C.sub)
      .id(id)
      .flex_none()
      .px(3)
      .h(15)
      .flex()
      .items_center()
      .border(1)
      .border_color(C.btnEdge)
      .cursor_pointer()
      .hover((el) => el.text_color(C.text).border_color(C.sub))
      .tooltip(tooltip)
      .on_click(onClick)
      .child(label);
  }

  // A group's header; a click collapses or opens the group.
  header(g, collapsed) {
    const { art, colors: C } = this.look;
    const ext = artExt(this.look);
    const busy = g.members.filter((a) => a.status === "working").length;
    return h_flex()
      .id(`group-${g.id}`)
      .flex_none()
      .h(30)
      .pt(6)
      .px(2)
      .gap(7)
      .items_center()
      .cursor_pointer()
      .tooltip(collapsed ? "Show the agents" : "Hide the agents")
      .on_click(() => toggle(COLLAPSED_KEY, g.id))
      .child(div().flex_none().text_color(C.sub).child(svg(`mods/workspace-chrome/${collapsed ? "chevron-right" : "chevron-down"}.svg`).size(12)))
      .child(image(`${art}/icon-machine-${g.scene.id}.${ext}`).w(15).h(11).flex_none())
      .child(this.pixel(div(), 11, g.color ?? C.machine).font_bold().truncate().child(g.label))
      .child(div().flex_1().min_w(8).h(2).bg(g.scene.edge))
      .child(this.pixel(div(), 11, g.scene.label).flex_none().child(`${busy}/${g.members.length}`));
  }

  // A small stage that focuses the agent's pane on a click.
  miniStage(a, scene) {
    const C = this.look.colors;
    return div()
      .id(`rail-${a.address}`)
      .flex_none()
      .border(2)
      .border_color(a.focused ? C.focus : C.clear)
      .cursor_pointer()
      .on_click(() => run("pane.focus", { pane: a.pane }))
      .on_mouse_down("right", (_e, cx) => this.openMenu(a, cx))
      .child(this.stage(a, scene, 36, 30, this.picked[a.address]));
  }

  openSpaceMenu(space, cx) {
    cx.stop_propagation();
    openOverlay({ mod: "menu", kind: "popup", width: 200, height: 260, props: { tab: "space", target: { id: space.id } } });
  }

  spaceRailCard(space, appTheme, buildingAssignments) {
    const C = this.look.colors;
    const color = this.spaceColor(space, appTheme);
    const activeBg = /^#[0-9a-f]{6}$/i.test(color) ? `${color}24` : C.divider;
    return div()
      .id(`space-rail-${space.id}`)
      .size(28)
      .flex_none()
      .flex()
      .items_center()
      .justify_center()
      .bg(space.active ? activeBg : C.bg)
      .border(1)
      .border_color(space.active ? color : C.btnEdge)
      .cursor_pointer()
      .tooltip(space.machine ? `${space.name} · ${space.machine}` : space.name)
      .on_click(() => run("space.select", { id: space.id }))
      .on_mouse_down("right", (_e, cx) => this.openSpaceMenu(space, cx))
      .child(this.spaceBuilding(space, color, buildingAssignments, 24, space.active));
  }

  newSpaceRailButton() {
    const C = this.look.colors;
    return div()
      .id("critters-space-new-rail")
      .size(28)
      .flex_none()
      .flex()
      .items_center()
      .justify_center()
      .rounded(6)
      .text_color(C.sub)
      .cursor_pointer()
      .hover((el) => el.bg(C.divider).text_color(C.text))
      .tooltip("New space")
      .on_click((_e, cx) => { cx.stop_propagation(); run("space.new"); })
      .child(svg("mods/workspace-chrome/plus.svg").size(14));
  }

  // The narrow rail keeps spaces selectable above the existing agent sprites.
  rail(list, sceneOf, spacesList, appTheme, buildingAssignments) {
    const C = this.look.colors;
    return v_flex()
      .size_full()
      .bg(C.bg)
      .items_center()
      .pt(8)
      .gap(6)
      .overflow_y_scrollbar()
      .children([
        this.newSpaceRailButton(),
        ...spacesList.map((space) => this.spaceRailCard(space, appTheme, buildingAssignments)),
        div().w(24).h(1).flex_none().bg(C.divider),
        ...list.map((a) => this.miniStage(a, sceneOf(a))),
      ]);
  }

  spaceColor(space, appTheme) {
    const assigned = (shared("space.colors") ?? {})[space.id];
    if (typeof assigned !== "string") return this.look.colors.machine;
    if (assigned.startsWith("#")) return assigned;
    return SPACE_MARK_COLORS[assigned] ?? appTheme[assigned] ?? this.look.colors.machine;
  }

  spaceBuildingAssignments(spacesList) {
    const stored = shared(SPACE_BUILDINGS_KEY);
    const assignments = stored && typeof stored === "object" && !Array.isArray(stored) ? { ...stored } : {};
    const valid = new Set(SPACE_BUILDINGS);
    const occupied = new Set(
      spacesList.map((space) => assignments[String(space.id)]).filter((name) => valid.has(name)),
    );
    let changed = false;

    for (const space of spacesList) {
      const id = String(space.id);
      if (valid.has(assignments[id])) continue;
      const start = spaceBuildingHash(id) % SPACE_BUILDINGS.length;
      let building = null;
      for (let offset = 0; offset < SPACE_BUILDINGS.length; offset++) {
        const candidate = SPACE_BUILDINGS[(start + offset) % SPACE_BUILDINGS.length];
        if (!occupied.has(candidate)) {
          building = candidate;
          break;
        }
      }
      if (!building) building = SPACE_BUILDINGS[start];
      assignments[id] = building;
      occupied.add(building);
      changed = true;
    }

    if (changed) setShared(SPACE_BUILDINGS_KEY, assignments);
    return assignments;
  }

  spaceBuilding(space, color, buildingAssignments, size = 24, active = false) {
    const building = buildingAssignments[String(space.id)]
      ?? SPACE_BUILDINGS[spaceBuildingHash(space.id) % SPACE_BUILDINGS.length];
    const scale = size / 24;
    return div().relative().size(size).flex_none()
      .opacity(active ? 1 : 0.55)
      .child(image(`${this.look.art}/space-${building}.svg`).size(size))
      .child(div().absolute()
        .left(Math.round(10 * scale))
        .top(Math.round(17 * scale))
        .w(Math.max(3, Math.round(4 * scale)))
        .h(Math.max(2, Math.round(2 * scale)))
        .bg(color)
        .when(active, (el) => el.loop("opacity", { from: 0.75, to: 1, period: 1800 })));
  }

  spaceStatusBox(space) {
    const C = this.look.colors;
    const status = space.status ? this.statusOf(space.status) : null;
    return this.pixel(div(), status ? 8 : 7, status?.color ?? C.sub)
      .flex_none()
      .px(4)
      .h(15)
      .flex()
      .items_center()
      .border(1)
      .border_color(status?.color ?? C.btnEdge)
      .child(status?.word ?? "NO AGENTS");
  }

  spaceSectionHeader(count, collapsed) {
    const C = this.look.colors;
    return h_flex()
      .id("critters-spaces-header")
      .flex_none()
      .h(28)
      .px(2)
      .gap(7)
      .items_center()
      .cursor_pointer()
      .tooltip(collapsed ? "Show spaces" : "Hide spaces")
      .on_click(() => toggle(SPACES_COLLAPSED_KEY, "spaces"))
      .child(div().flex_none().text_color(C.sub).child(svg(`mods/workspace-chrome/${collapsed ? "chevron-right" : "chevron-down"}.svg`).size(12)))
      .child(this.pixel(div(), 11, C.head).font_bold().child("SPACES"))
      .child(div().flex_1().min_w(8).h(1).bg(C.divider))
      .child(this.pixel(div(), 10, C.sub).flex_none().child(String(count)))
      .child(div().id("critters-space-new").size(20).flex_none().flex().items_center().justify_center().rounded(4)
        .text_color(C.sub).cursor_pointer().hover((el) => el.bg(C.divider).text_color(C.text))
        .tooltip("New space")
        .on_click((_e, cx) => { cx.stop_propagation(); run("space.new"); })
        .child(svg("mods/workspace-chrome/plus.svg").size(13)));
  }

  agentsSectionHeader(bySpace) {
    const C = this.look.colors;
    return h_flex()
      .id("critters-agents-header")
      .flex_none()
      .h(28)
      .pt(4)
      .px(2)
      .gap(6)
      .items_center()
      .child(this.pixel(div(), 11, C.head).font_bold().child("AGENTS"))
      .child(div().flex_1().min_w(8).h(1).bg(C.divider))
      .child(this.headerButton(
        "critters-group",
        "Group agents by machine or by space",
        () => setShared(GROUP_KEY, bySpace ? "machine" : "space"),
        bySpace ? "BY SPACE" : "BY MACHINE",
      ));
  }

  // How much to scale the city so it fills the sidebar: 1 at 240 px.
  cityScale() {
    const px = find(layout(), "sidebar")?.size?.px ?? 268;
    return Math.max(0.6, Math.min(1.6, (px - 28) / CITY.canvas.w));
  }

  // The Spaces section: one isometric city. Each of the first eight spaces is a
  // building on a lot, in space order, back to front.
  city(spacesList, appTheme, buildingAssignments) {
    const { art, colors: C, status: STATUS } = this.look;
    const k = this.cityScale();
    const px = (v) => Math.round(v * k);
    const { canvas, building: BLD, lots, types } = CITY;
    const shown = spacesList.slice(0, lots.length);
    const stage = div().relative().w(px(canvas.w)).h(px(canvas.h)).flex_none()
      .child(image(`${art}/city-plate.svg`).absolute().left(0).top(0).w(px(canvas.w)).h(px(canvas.h)));
    const typeOf = (space) => buildingAssignments[String(space.id)]
      ?? SPACE_BUILDINGS[spaceBuildingHash(space.id) % SPACE_BUILDINGS.length];

    // Buildings, back to front.
    lots.forEach((lot, i) => {
      const space = shown[i];
      const art_ = space ? typeOf(space) : `empty-${EMPTY_ORDER[i] % CITY.empties}`;
      stage.child(image(`${art}/city-${art_}.svg`).absolute()
        .left(px(lot.x)).top(px(lot.y)).w(px(BLD.w)).h(px(BLD.h)));
    });

    // Flags, status badges and the active arrow sit above every roof.
    const overlays = [];
    const hits = [];
    lots.forEach((lot, i) => {
      const space = shown[i];
      if (!space) {
        hits.push(div().id(`city-empty-${i}`).absolute()
          .left(px(lot.x + 14)).top(px(lot.y + BLD.top - 4)).w(px(BLD.w - 28)).h(px(30))
          .cursor_pointer().tooltip("New space")
          .on_click((_e, cx) => { cx.stop_propagation(); run("space.new"); }));
        return;
      }
      const meta = types[typeOf(space)];
      const color = this.spaceColor(space, appTheme);
      const fx = lot.x + meta.flag[0];
      const fy = lot.y + meta.flag[1];
      overlays.push(div().absolute().left(px(fx)).top(px(fy) - 10).w(1).h(10).bg(C.text));
      let flag = div().absolute().left(px(fx) + 1).top(px(fy) - 10).w(7).h(5).bg(color);
      if (space.active) flag = flag.loop("opacity", { from: 0.6, to: 1, period: 1200 });
      overlays.push(flag);
      // Status, quietly: smoke while working, a pulsing red light when blocked,
      // a steady green light when done. Idle shows nothing.
      const st = space.status;
      if (st === "working") {
        const [sx, sy] = [px(lot.x + meta.smoke[0]), px(lot.y + meta.smoke[1])];
        // Three puffs drifting up and a little to the right, each on its own beat.
        [[0, -1, 3, 2300], [2, -6, 4, 2900], [5, -12, 5, 3500]].forEach(([dx, dy, size, period], n) => {
          const top = sy + dy - size;
          overlays.push(div().id(`city-smoke-${space.id}-${n}`).absolute().left(sx + dx - size / 2).top(top)
            .size(size).rounded_full().bg(C.text)
            .loop("top", { from: top, to: top - 3, period })
            .loop("opacity", { from: 0.12, to: 0.4, period: period * 0.8 }));
        });
      } else if (st === "blocked" || st === "done") {
        let light = div().absolute().left(px(fx) - 1).top(px(fy) - 13).size(3).rounded_full().bg(STATUS[st].color);
        if (st === "blocked") light = light.loop("opacity", { from: 0.2, to: 1, period: 900 });
        overlays.push(light);
      }
      if (space.active) {
        // Above the roof, and above the smoke when there is some.
        const roof = px(lot.y + meta.top);
        const top = st === "working" ? Math.min(roof, px(lot.y + meta.smoke[1]) - 20) : roof;
        overlays.push(div().id(`city-arrow-${space.id}`).absolute().left(px(lot.x + BLD.w / 2) - 6).top(top - 16).w(12).h(12)
          .loop("top", { from: top - 18, to: top - 13, period: 900 })
          .text_color(C.focus).child(svg("mods/workspace-chrome/chevron-down.svg").size(12)));
      }
      hits.push(div().id(`city-bld-${space.id}`).absolute()
        .left(px(lot.x + 8)).top(px(lot.y + meta.top)).w(px(BLD.w - 16)).h(px(BLD.h - 4 - meta.top))
        .cursor_pointer()
        .on_hover((on, cx) => {
          if (on) this.hoverSpace = space.id;
          else if (this.hoverSpace === space.id) this.hoverSpace = null;
          cx.notify();
        })
        .on_click(() => run("space.select", { id: space.id }))
        .on_mouse_down("right", (_e, cx) => this.openSpaceMenu(space, cx)));
    });

    return stage.children(overlays).children(hits);
  }

  // Under the city: the hovered space, else the active one, with its details.
  cityCaption(space, appTheme, agentCount) {
    const C = this.look.colors;
    if (!space) return div();
    const folder = (space.folder ?? "").split(/[\\/]+/).filter(Boolean).at(-1) ?? "";
    const location = space.branch || (folder && folder.toLowerCase() !== space.name.toLowerCase() ? folder : "");
    const tabCount = space.tabs.length;
    const counts = `${tabCount} ${tabCount === 1 ? "tab" : "tabs"} · ${agentCount} ${agentCount === 1 ? "agent" : "agents"}`;
    return v_flex().flex_none().gap(3).px(4)
      .child(h_flex().gap(6).items_center().min_w(0)
        .child(div().size(8).flex_none().bg(this.spaceColor(space, appTheme)))
        .child(div().flex_1().min_w(0).font_family(this.look.fonts.mono).text_size(18).line_height("17px").text_color(C.text).truncate().child(space.name))
        .child(this.spaceStatusBox(space)))
      .child(h_flex().gap(4).items_center().min_w(0)
        .child(svg(`mods/herdr-critters/icons/${space.machine ? "network" : "laptop"}.svg`).size(11).flex_none().text_color(C.sub))
        .child(div().flex_1().min_w(0).text_size(11).text_color(C.sub).truncate().child([location, counts].filter(Boolean).join(" · "))));
  }

  // Spaces past the city's eight lots, one line each.
  overflowRow(space, appTheme, buildingAssignments) {
    const C = this.look.colors;
    const color = this.spaceColor(space, appTheme);
    return h_flex().id(`space-row-${space.id}`).flex_none().h(24).px(4).gap(6).items_center()
      .border(1).border_color(space.active ? color : C.btnEdge)
      .cursor_pointer().hover((el) => el.bg(C.divider))
      .on_click(() => run("space.select", { id: space.id }))
      .on_mouse_down("right", (_e, cx) => this.openSpaceMenu(space, cx))
      .child(this.spaceBuilding(space, color, buildingAssignments, 16, space.active))
      .child(div().flex_1().min_w(0).font_family(this.look.fonts.mono).text_size(16).line_height("15px").text_color(C.text).truncate().child(space.name))
      .child(this.spaceStatusBox(space));
  }

  render() {
    const look = activeTheme();
    this.useTheme(look);
    if (props()?.menu) return this.menu(props().menu);
    const { colors: C, status: STATUS } = look;
    const t = theme();
    const spacesList = spaces();
    const buildingAssignments = this.spaceBuildingAssignments(spacesList);
    const allAgents = agents();
    const spacesById = new Map(spacesList.map((space) => [space.id, space]));
    const order = [null, ...machines().map((m) => m.name).filter((n) => n !== null)];
    const sceneOf = (a) => {
      const m = machineOf(a);
      const id = m === null ? look.localScene : look.remoteScenes[Math.max(0, order.indexOf(m) - 1) % look.remoteScenes.length];
      return { id, ...look.scenes[id] };
    };

    // agents() comes in machine, space order, so neighbours make a group either way.
    // Pins go first inside their group.
    const bySpace = groupBy() === "space";
    const groups = [];
    for (const a of allAgents) {
      const m = machineOf(a);
      const key = bySpace ? a.space : m;
      if (groups.at(-1)?.key === key) {
        groups.at(-1).members.push(a);
        continue;
      }
      const scene = sceneOf(a);
      const space = spacesById.get(a.space);
      groups.push(bySpace
        ? { key, id: groupIdOf(a), label: (a.space_name || "space").toUpperCase(), color: space ? this.spaceColor(space, t) : C.machine, scene, members: [a] }
        : { key, id: groupIdOf(a), label: m === null ? "THIS MACHINE" : m.toUpperCase(), scene, members: [a] });
    }
    for (const g of groups) g.members = [...g.members.filter((a) => a.pinned), ...g.members.filter((a) => !a.pinned)];
    const list = groups.flatMap((g) => g.members);
    setAgentOrder(list.map((a) => a.address));

    const names = this.names(list);
    if (narrow()) return this.rail(list, sceneOf, spacesList, t, buildingAssignments);

    const all = terminals();
    const tabs = spacesList.flatMap((s) => s.tabs);
    const busy = allAgents.filter((a) => a.status === "working").length;
    const byAddress = new Map(all.map((t) => [t.address, t]));
    const agentCounts = new Map();
    for (const a of allAgents) agentCounts.set(a.space, (agentCounts.get(a.space) ?? 0) + 1);

    // A collapsed group shows only its header.
    const rows = groups.flatMap((g) => {
      const collapsed = isSet(COLLAPSED_KEY, g.id);
      return [
        this.header(g, collapsed),
        ...(collapsed ? [] : g.members.map((a) => this.card(a, g.scene, tabs, names.get(a.address), sessionName(a, byAddress.get(a.address))))),
      ];
    });

    const spacesCollapsed = isSet(SPACES_COLLAPSED_KEY, "spaces");
    const captioned = spacesList.find((space) => space.id === this.hoverSpace) ?? spacesList.find((space) => space.active);
    const overflow = spacesList.slice(CITY.lots.length);
    const spaceContent = spacesList.length === 0
      ? v_flex().px(14).pt(4).child(this.pixel(div(), 11, C.machine).child("NO SPACES YET"))
      : v_flex().gap(6)
        .child(h_flex().justify_center().child(this.city(spacesList, t, buildingAssignments)))
        .child(this.cityCaption(captioned, t, agentCounts.get(captioned?.id) ?? 0))
        .children(overflow.map((space) => this.overflowRow(space, t, buildingAssignments)));
    const spacesSection = v_flex().gap(4).children([
      this.spaceSectionHeader(spacesList.length, spacesCollapsed),
      ...(spacesCollapsed ? [] : [spaceContent]),
    ]);
    const agentsContent = list.length === 0
      ? v_flex().px(14).pt(4).gap(6)
        .child(this.pixel(div(), 11, C.machine).child("NO PLAYERS YET"))
        .child(div().text_size(11.5).text_color(C.sub).child("Agents show up here when they report their status."))
      : v_flex().gap(8).children(rows);
    const agentsSection = v_flex().gap(4)
      .child(this.agentsSectionHeader(bySpace))
      .child(agentsContent);

    return v_flex()
      .size_full()
      .min_h(0)
      .bg(C.bg)
      .border_t(1)
      .border_color(C.divider)
      .child(
        h_flex()
          .flex_none()
          .h(38)
          .px(14)
          .pt(6)
          .items_center()
          .justify_between()
          .child(h_flex().flex_none().gap(5).items_center()
            .child(image(`${look.art}/icon-dither.${artExt(look)}`).size(12).flex_none())
            .child(this.headerButton("critters-theme", "Switch the look of the cards", () => setShared(THEME_KEY, THEMES[(THEMES.indexOf(look) + 1) % THEMES.length].id), look.label)))
          .child(this.pixel(div(), 11, busy ? STATUS.working.color : C.head).flex_none().child(`${busy} ${STATUS.working.word}`)),
      )
      .child(v_flex().id("critters-list").flex_1().min_h(0).px(10).pb(10).gap(8).overflow_y_scrollbar()
        .children([spacesSection, agentsSection]));
  }
}
