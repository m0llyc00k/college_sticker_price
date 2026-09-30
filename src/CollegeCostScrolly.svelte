<script>
  /**
   * CollegeCostScrolly.svelte — LayerCake + Scrollama scrollytelling (7 steps).
   * Pinned bar chart: sticker "ghost" (light) + cost-after-aid "fill" (dark),
   * with arrow annotations for individual-college callouts.
   * Requires: layercake, d3-scale, d3-format, scrollama.
   * Load DM Sans once in your app <head>:
   *   <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
   */
  import { onMount } from "svelte";
  import { LayerCake, Svg } from "layercake";
  import { scaleBand, scaleLinear } from "d3-scale";
  import scrollama from "scrollama";
  import Bars from "./Bars.svelte";
  import AxisY from "./AxisY.svelte";
  import Annotations from "./Annotations.svelte";
  import { colleges } from "./data.js";

  export let data = colleges;

  const AXIS_MAX = 120000;
  const TICKS = [0, 20000, 40000, 60000, 80000, 100000, 120000];

  // LayerCake wants an x key; add the row index.
  $: rows = data.map((d, i) => ({ ...d, i }));

  // groups / individuals referenced by the steps
  const one = (name) => data.findIndex((d) => d.n.startsWith(name));
  $: over100 = new Set(data.map((d, i) => (d.s > 100000 ? i : -1)).filter((i) => i >= 0));
  $: near99  = new Set(data.map((d, i) => (d.s >= 99000 && d.s < 100000 ? i : -1)).filter((i) => i >= 0));
  $: iChicago   = one("University of Chicago");
  $: iPrinceton = one("Princeton");
  $: iPepp      = one("Pepperdine");
  $: iNew       = one("The New School");

  const CAPS = [
    "Here are the 100 most expensive colleges for the 2026-2027 year.",
    "16 colleges now list a cost of attendance over $100,000 a year.",
    "11 more hover just below six figures, around $99,000.",
    "But once average aid is applied, the price students actually pay is significantly less.",
    "The University of Chicago lists a cost of attendance of $103,821 — but about $17,074 after aid.",
    "Princeton gives the biggest discount, an average net price of about $6,900, more than 90% less than the original sticker price.",
    "Pepperdine and The New School have the smallest reduction, both remain above $60,000 per year."
  ];

  // ---- per-step chart state ----
  // step 0 intro (all sticker) · 1 the 16 · 2 the 11 · 3 aid applied (all net)
  // · 4 Chicago · 5 Princeton · 6 Pepperdine + The New School
  let step = 0;
  $: dropped = step >= 3;                    // aid applied from step 4 (index 3) onward
  $: emphAll = step === 0 || step === 3;     // intro = all sticker bars; step 3 = all net bars
  $: emphSet =
      step === 1 ? over100 :
      step === 2 ? near99 :
      step === 4 ? new Set([iChicago]) :
      step === 5 ? new Set([iPrinceton]) :
      step === 6 ? new Set([iPepp, iNew]) :
      new Set();
  $: annItems =
      step === 4 ? [{ i: iChicago, title: "University of Chicago" }] :
      step === 5 ? [{ i: iPrinceton, title: "Princeton" }] :
      step === 6 ? [{ i: iPepp, title: "Pepperdine" }, { i: iNew, title: "The New School" }] :
      [];

  onMount(() => {
    const scroller = scrollama();
    scroller
      .setup({ step: ".step", offset: 0.6, debug: false })
      .onStepEnter(({ index }) => { step = index; });
    const onResize = () => scroller.resize();
    window.addEventListener("resize", onResize);
    return () => { window.removeEventListener("resize", onResize); scroller.destroy(); };
  });
</script>

<section class="scrolly">
  <div class="chart-sticky">
    <div class="chart">
      <LayerCake
        padding={{ top: 28, right: 16, bottom: 28, left: 84 }}
        x="i"
        y="s"
        data={rows}
        xScale={scaleBand().paddingInner(0.22)}
        yScale={scaleLinear()}
        yDomain={[0, AXIS_MAX]}
      >
        <Svg>
          <AxisY ticks={TICKS} refValue={100000} />
          <Bars {dropped} {emphAll} {emphSet} />
          <Annotations items={annItems} />
        </Svg>
      </LayerCake>
    </div>
  </div>

  <div class="steps">
    {#each CAPS as caption, i}
      <div class="step">
        <div class="box" class:active={step === i}>{caption}</div>
      </div>
    {/each}
  </div>
</section>

<style>
  .scrolly{
    --vh: 92vh;                 /* pinned-area height; leaves room for site header */
    --maxw: min(1100px, 92vw);  /* chart + caption column width cap */
    position:relative;
    --ink:#182420;
    font-family:"DM Sans",system-ui,sans-serif;
    background:#fff;color:var(--ink);
    font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased;
    text-align:left;direction:ltr;          /* anchor alignment context */
  }
  @supports (height:100dvh){
    .scrolly{ --vh: 92dvh; }    /* mobile-safe unit, same size */
  }

  /* --- isolate from the host site's global CSS --- */
  .scrolly, .scrolly *{
    box-sizing:border-box; margin:0; padding:0;
    text-align:inherit;
  }
  .scrolly :where(svg, text, line, rect, tspan){ all: revert; }

  /* --- pinned graphic, centered in the frame --- */
  .chart-sticky{
    position:sticky;
    top:10%;
    height:var(--vh);
    width:100%;
    display:flex;align-items:center;justify-content:center;
  }
  .chart{
    width:var(--maxw);
    height:min(80%, 720px);
  }

  /* --- steps overlaid on the pinned chart --- */
  .steps{
    position:relative;
    margin:calc(var(--vh) * -1) auto 0;    /* top pull-up + horizontal auto-center */
    z-index:2;pointer-events:none;
    width:var(--maxw);
    max-width:100%;
  }
  .step{
    min-height:var(--vh);
    display:block;                          /* box centered via margin auto, not flex */
    padding:12vh 0 0;
  }
  .box{
    margin:0 auto;                          /* center the box in the column */
    pointer-events:auto;
    width:fit-content;max-width:30ch;
    background:rgba(255,255,255,.82);
    -webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);
    border:1px solid #e6ebe8;border-radius:12px;
    padding:.7rem 1rem;
    font-weight:600;font-size:clamp(1rem,2vw,1.5rem);
    line-height:1.16;letter-spacing:-.02em;
    opacity:.35;transition:opacity .3s ease;
  }
  .box.active{opacity:1}

  @media (max-width:720px){
    .scrolly{ --maxw: 100%; }
    .step{ padding:9vh 12px 0; }            /* top + small side gutter */
    .box{ max-width:100%; }
  }
</style>