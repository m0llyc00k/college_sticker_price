import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import cssInjectedByJsPlugin from "vite-plugin-css-injected-by-js";
import { fileURLToPath } from "node:url";

export default defineConfig({
  plugins: [svelte(), cssInjectedByJsPlugin()],
  resolve: {
    alias: { furniture: fileURLToPath(new URL("../furniture", import.meta.url)) },
  },
  server: { fs: { allow: [".."] } },
  build: {
    outDir: "embed",
    emptyOutDir: true,
    lib: {
      entry: "src/embed.js",
      name: "CollegeCost",
      fileName: () => "college-cost.js",
    },
  },
});