# College Cost Scrollytelling

An interactive, scroll-driven bar chart of the **100 most expensive U.S. private
colleges** (projected 2026–27). As you scroll, each bar's sticker price ("cost of
attendance") drops to the net price students actually pay after average grant aid,
with callouts for specific schools.

Built with **Svelte + LayerCake + Scrollama**, and packaged as a single
self-contained JavaScript file you can embed anywhere (Webflow, any CMS, a plain
HTML page).

---

## 1. Requirements

- [Node.js](https://nodejs.org) 18 or newer. Check with:
  ```bash
  node -v
  ```

## 2. Install

From the project folder:
```bash
npm install
```
This pulls Svelte, Vite, LayerCake, d3-scale, d3-format, Scrollama, and the
css-inject build plugin.

## 3. Run locally (development)

```bash
npm run dev
```
Open the URL Vite prints (default **http://localhost:5173**) and scroll. The page
hot-reloads as you edit files in `src/`.

## 4. Build the embeddable file

```bash
npm run build
```
This produces one self-contained file:
```
embed/college-cost.js
```
Everything is baked in — the Svelte runtime, LayerCake, d3, Scrollama, your data,
and all CSS. It mounts into an element with `id="college-cost"` and loads the
DM Sans font itself. There is **no separate CSS file** to manage.

---

## Project structure

```
college_cost_app/
├─ index.html                 # local dev page (mounts #college-cost)
├─ package.json               # scripts + dependencies
├─ vite.config.js             # dev server + single-file embed build
├─ README.md
├─ embed/
│  └─ college-cost.js         # ← the built file you host (created by `npm run build`)
└─ src/
   ├─ embed.js                # entry: mounts the chart into #college-cost, loads the font
   ├─ data.js                 # the 100-college dataset  { n: name, s: sticker, net: net }
   ├─ CollegeCostScrolly.svelte # main component: steps, scroll logic, layout, styles
   ├─ Bars.svelte             # the bars (sticker "ghost" + net "fill")
   ├─ AxisY.svelte            # dollar gridlines, labels, $100k dashed line
   └─ Annotations.svelte      # per-college arrow callouts
```

### Where to change things
- **The story / captions / which step highlights what** → `src/CollegeCostScrolly.svelte`
  (the `CAPS` array and the per-step `dropped` / `emphAll` / `emphSet` / `annItems` logic).
- **The data** → `src/data.js`.
- **Chart look** (bars, axis, annotations) → `Bars.svelte`, `AxisY.svelte`, `Annotations.svelte`.
- **Layout, sizing, centering, caption styling** → the `<style>` block in
  `CollegeCostScrolly.svelte` (tune the `--vh` and `--maxw` variables at the top).

---

## Deploy & embed (Webflow or any site)

The built file is just a script, so you host it and reference it with a `<script>` tag.

### Step 1 — build
```bash
npm run build
```

### Step 2 — push to GitHub and tag a version
Commit the built file, then tag it. **Tags matter:** the CDN caches the `main`
branch for up to 12 hours, but a version tag is immutable and always fresh.
```bash
git add -A
git commit -m "build"
git push
git tag v1 && git push --tags
```
(Next time you ship a change, bump to `v2`, `v3`, …)

### Step 3 — get the public URL (via jsDelivr, free CDN)
```
https://cdn.jsdelivr.net/gh/USER/REPO@v1/embed/college-cost.js
```
Replace `USER/REPO` with your GitHub account/repo. Paste that URL into a browser
first to confirm it loads JavaScript before embedding.

### Step 4 — embed
In a **Webflow Code Embed** (or any HTML page), paste exactly:
```html
<div id="college-cost"></div>
<script src="https://cdn.jsdelivr.net/gh/USER/REPO@v1/embed/college-cost.js"></script>
```
- Do **not** wrap it in `<html>`/`<head>`/`<body>` — a Code Embed is a fragment.
- Embeds don't run in the Webflow Designer — use **Preview** or **Publish** to see it.
- Give it its own full-width section; don't nest it in a container with
  `overflow: hidden` or a fixed height (it uses full-height sticky scroll).

---

## Updating after a change

The CSS and everything else live **inside** `embed/college-cost.js`, so you must
rebuild after any edit — editing `src/` alone does nothing on the live site.

```bash
npm run build                        # regenerate embed/college-cost.js
git add -A && git commit -m "update" && git push
git tag v2 && git push --tags        # bump the version
```
Then change `@v1` → `@v2` in your embed.

**Shortcut:** a `ship` script is handy so you can't forget the build step. Add to
`package.json`:
```json
"scripts": {
  "ship": "npm run build && git add -A && git commit -m \"rebuild\" && git push"
}
```
Then just `npm run ship` (and bump the tag when you want the CDN to refresh).

### Forcing the CDN to refresh
If you stay on `@main` instead of tags, bust jsDelivr's cache by opening this once:
```
https://purge.jsdelivr.net/gh/USER/REPO@main/embed/college-cost.js
```

---

## Share a standalone link (no Webflow)

To send someone the chart on its own page, enable **GitHub Pages**:

1. Add `docs/index.html`:
   ```html
   <!doctype html>
   <html lang="en"><head>
     <meta charset="utf-8">
     <meta name="viewport" content="width=device-width, initial-scale=1">
   </head><body style="margin:0">
     <div id="college-cost"></div>
     <script src="https://cdn.jsdelivr.net/gh/USER/REPO@v1/embed/college-cost.js"></script>
   </body></html>
   ```
2. GitHub → **Settings → Pages → Source: Deploy from a branch → `main` / `/docs`**.
3. Share the URL it gives you: `https://USER.github.io/REPO/`

---

## Troubleshooting

- **Webflow shows old styles after an update** → you forgot `npm run build`, or the
  CDN is serving a cached `@main`. Rebuild, push, then bump the tag (or purge).
- **CORS / "unable to load external script"** → don't use `raw.githubusercontent.com`;
  use the `cdn.jsdelivr.net` URL.
- **Nothing renders** → confirm the page has `<div id="college-cost"></div>` and the
  script URL loads JS in a browser tab.
- **Chart cut off / not centered in the host page** → tune `--vh` (pinned height)
  and `--maxw` (width) at the top of the `<style>` block in `CollegeCostScrolly.svelte`,
  then rebuild.

## Tech stack
- [Svelte](https://svelte.dev) + [Vite](https://vitejs.dev)
- [LayerCake](https://layercake.graphics) for chart scales/layout
- [Scrollama](https://github.com/russellsamora/scrollama) for scroll steps
- [d3-scale](https://github.com/d3/d3-scale) + [d3-format](https://github.com/d3/d3-format)
- [vite-plugin-css-injected-by-js](https://github.com/marco-prontera/vite-plugin-css-injected-by-js) to bundle CSS into the single file