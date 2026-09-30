import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import cssInjectedByJsPlugin from "vite-plugin-css-injected-by-js";

// `npm run dev`   -> local dev server (uses index.html)
// `npm run build` -> single self-contained embed/college-cost.js (CSS baked in)
export default defineConfig({
  plugins: [svelte(), cssInjectedByJsPlugin()],
  build: {
    outDir: "embed",
    emptyOutDir: true,
    lib: {
      entry: "src/embed.js",
      name: "CollegeCost",
      formats: ["iife"],
      fileName: () => "college-cost.js"
    }
  }
});
