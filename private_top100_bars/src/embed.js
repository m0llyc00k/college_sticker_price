// Embed entry point. Builds to a single self-contained script (embed/college-cost.js)
// that mounts the graphic into <div id="college-cost"></div> wherever it appears.
import CollegeCostScrolly from "./CollegeCostScrolly.svelte";

// Make sure DM Sans is loaded on the host page (Webflow, etc.) — injected once.
const FONT = "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap";
if (!document.querySelector(`link[href="${FONT}"]`)) {
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = FONT;
  document.head.appendChild(link);
}

function mount() {
  const target = document.getElementById("college-cost");
  if (!target || target.dataset.mounted) return; // guard against double-mount
  target.dataset.mounted = "true";
  new CollegeCostScrolly({ target });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mount);
} else {
  mount();
}
