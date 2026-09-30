# College cost scrollytelling — Svelte + LayerCake + Scrollama

A pinned bar chart of the 100 most expensive US private colleges: sticker price
("ghost") drops to net price after aid, with per-college arrow annotations,
driven by scroll. Built to embed cleanly into Webflow (or any CMS).

## Requirements
- Node.js 18+

## Install
```bash
npm install
```

## Run locally
```bash
npm run dev
```
Open the URL Vite prints (default http://localhost:5173) and scroll.
Edit anything in `src/` — it hot-reloads.

- Story steps + per-step chart logic: `src/CollegeCostScrolly.svelte`
- The data: `src/data.js`
- Chart pieces: `src/Bars.svelte`, `src/AxisY.svelte`, `src/Annotations.svelte`

## Build the embeddable file
```bash
npm run build
```
This produces a single, self-contained script (CSS baked in):
```
embed/college-cost.js
```
That one file is everything — Svelte runtime, LayerCake, d3, Scrollama, your
data and styles. It mounts into an element with id `college-cost` and self-loads
the DM Sans font.

## Host it
Commit `embed/college-cost.js` to a public GitHub repo, then serve it free via
jsDelivr. Tag a version so the URL is stable:
```bash
git add embed/college-cost.js && git commit -m "build" && git push
git tag v1 && git push --tags
```
Your file is then at:
```
https://cdn.jsdelivr.net/gh/USER/REPO@v1/embed/college-cost.js
```
(Any static host works too — Netlify, S3, Cloudflare Pages. Just get a URL to
the file.)

## Embed in Webflow
Add a **Code Embed** element where you want the graphic and paste:
```html
<div id="college-cost"></div>
<script src="https://cdn.jsdelivr.net/gh/USER/REPO@v1/embed/college-cost.js"></script>
```
- Embeds don't render in the Webflow Designer — use **Preview** or **Publish**.
- The graphic uses full-height sticky scroll, so give it its own section (don't
  nest it inside a container with `overflow: hidden` or a fixed height).
- No iframe: it mounts into the page so the sticky + scroll steps work with the
  page's own scroll.

## Update the graphic later
1. Edit `src/…`, run `npm run build` again.
2. Commit, bump the tag (`v2`), push tags.
3. Change `@v1` to `@v2` in the Webflow embed (bumping the tag also busts
   jsDelivr's cache).

## Notes
- `src/CollegeCostBars.svelte` is an older, from-scratch (non-LayerCake) version
  kept for reference; it isn't used by the build and can be deleted.
