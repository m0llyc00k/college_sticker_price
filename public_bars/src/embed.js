// Embed entry. Builds to a single self-contained script (embed/public-cost.js).
// Renders the public-university chart into <div id="public-cost">.
import PublicCostScrolly from "./PublicCostScrolly.svelte";

const FONT = "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap";
if (!document.querySelector(`link[href="${FONT}"]`)) {
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = FONT;
  document.head.appendChild(link);
}

function mount() {
  const target = document.getElementById("public-cost");
  if (!target || target.dataset.mounted) return;
  target.dataset.mounted = "true";
  new PublicCostScrolly({ target });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mount);
} else {
  mount();
}
