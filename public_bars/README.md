# Public college cost — standalone embed

Scrollytelling bar chart of the 20 most expensive public universities (2026–27):
sticker price drops to net price after aid, with a shaded $20k–$29k band marking
what people assume public college costs.

## Run locally
```bash
npm install
npm run dev
```

## Build the embeddable file
```bash
npm run build      # -> embed/public-cost.js  (single self-contained file)
```

## Embed (Webflow or any page)
Host `embed/public-cost.js` (e.g. GitHub + jsDelivr), then:
```html
<div id="public-cost"></div>
<script src="https://cdn.jsdelivr.net/gh/USER/REPO@v1/embed/public-cost.js"></script>
```

Edit the story in `src/PublicCostScrolly.svelte` (the `CAPS` array) and the data in
`src/public-data.js`. Rebuild, commit, bump the version tag.
