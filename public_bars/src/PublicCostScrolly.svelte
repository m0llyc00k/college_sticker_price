<script>
  /**
   * PublicCostScrolly.svelte — LayerCake + Scrollama scrollytelling.
   * Full population of public universities (IPEDS), in-state. Sticker "ghost"
   * drops to net "fill". A shaded zone marks the ">$20,000 a year" that a 2025
   * Strada survey found people expect; the split is at $20,000.
   * Requires: layercake, d3-scale, d3-format, scrollama.
   */
  import { onMount } from "svelte";
  import { LayerCake, Svg } from "layercake";
  import { scaleBand, scaleLinear } from "d3-scale";
  import scrollama from "scrollama";
  import Bars from "furniture/Bars.svelte";
  import AxisY from "furniture/AxisY.svelte";
  import Band from "furniture/Band.svelte";
  import BandLabels from "furniture/BandLabels.svelte";
  import { publics } from "./public-data.js";

  export let data = publics;

  const AXIS_MAX = 50000;
  const TICKS = [0, 10000, 20000, 30000, 40000, 50000];
  const LINE = 20000;   // the $20k split people assume

  let annotation = '$20,000 per year cost of attendance'

  // stable id up front so bars keep identity across re-sorts
  $: base = data.map((d, id) => ({ ...d, id }));

  const CAPS = [
    "These are the 2024–25 sticker prices for every public university in the IPEDS database.",
    "As with private universities, the real cost drops significantly once average grant aid is applied.",
    "In a 2025 Strada survey, almost 80% of respondents thought public four-year colleges cost more than $20,000 a year.",
    "But roughly 87% actually cost less than $20,000 a year after aid.",
    "Only about 13% — 72 of them — cost more than $20,000."
  ];

  // ---- per-step chart state ----
  // 0 intro (sticker) · 1 aid applied (net) · 2 "expected" zone >$20k (survey)
  // · 3 below $20k · 4 above $20k
  let step = 0;
  $: dropped = step >= 1;
  $: emphAll = step <= 2;
  $: mode = step === 3 ? "below" : step === 4 ? "above" : null;
  $: isEmph = (d) =>
      emphAll ||
      (mode === "below" && d.net < LINE) ||
      (mode === "above" && d.net > LINE);
  $: showBand = step >= 1;                       

  // sort: net price, highest first (no re-sort on scroll)
  $: sortKey = "net";
  $: sortDesc = true;
  $: rows = [...base]
      .sort((a, b) => (sortDesc ? b[sortKey] - a[sortKey] : a[sortKey] - b[sortKey]))
      .map((d, i) => ({ ...d, i }));

  onMount(() => {
    const scroller = scrollama();
    scroller
      .setup({ step: ".step--public", offset: 0.6, debug: false })
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
        xScale={scaleBand().paddingInner(0.1)}
        yScale={scaleLinear()}
        yDomain={[0, AXIS_MAX]}
      >
        <Svg>
          <AxisY ticks={TICKS} refValue={showBand ? LINE : null} {step} {annotation} {showBand} />
          <!-- <Band lo={LINE} hi={AXIS_MAX} show={showBand} label="what most people expect to pay" /> -->
          <Bars {dropped} {isEmph}  />
          <BandLabels show={step === 1} />
        </Svg>
      </LayerCake>
    </div>
  </div>

  <div class="steps">
    {#each CAPS as caption, i}
      <div class="step step--public">
        <div class="box" class:active={step === i}>{caption}</div>
      </div>
    {/each}
  </div>
</section>

<style>
   .scrolly{position:relative;--ink:#182420;
    font-family:"DM Sans",system-ui,sans-serif;background:#fff;color:var(--ink);
    font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}

  /* pinned graphic */
  .chart-sticky{position:sticky;top:0;height:100vh;width:100%}
  .chart{position:absolute;inset:clamp(16px,3vh,32px) clamp(16px,4vw,48px);}

  /* steps overlaid on the pinned chart */
  .steps{position:relative;margin-top:-100vh;z-index:2;pointer-events:none}
  .step{min-height:100vh;display:flex;align-items:flex-start;padding:12vh clamp(18px,5vw,64px) 0}
  .box{margin:0 auto; text-align:left;pointer-events:auto;max-width:30ch;background:rgba(255,255,255,.82);
    -webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);
    border:1px solid #e6ebe8;border-radius:12px;padding:.7rem 1rem;
    font-weight:600;font-size:clamp(1.2rem,2.7vw,2.1rem);line-height:1.16;letter-spacing:-.02em;
    opacity:.35;transition:opacity .3s ease}
  .box.active{opacity:1}

  @media (max-width:720px){
    .chart{inset:12px 10px;}
    .step{padding-top:9vh}
    .box{max-width:24ch}
  }
</style>