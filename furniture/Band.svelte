<script>
  /** LayerCake <Svg> child: a shaded horizontal reference band between two dollar
   *  values, with a label. Used to mark the "what most people expect to pay" zone. */
  import { getContext } from "svelte";
  export let lo = 20000;
  export let hi = 29000;
  export let show = false;
  export let label = "";
  const { yScale, width } = getContext("LayerCake");
  $: yHi = $yScale(hi);
  $: yLo = $yScale(lo);
</script>

{#if show}
  <g class="band">
    <!-- <rect class="band-fill" x="0" y={yHi} width={$width} height={yLo - yHi} /> -->
    <!-- <line class="band-edge" x1="0" x2={$width} y1={yHi} y2={yHi} /> -->
    <line class="band-edge" x1="0" x2={$width} y1={yLo} y2={yLo} />
    {#if label}
      <text class="band-label" x={$width} y={yHi - 8} text-anchor="end">{label}</text>
    {/if}
  </g>
{/if}

<style>
  /* .band-fill  { fill: rgba(0,122,88,.09); } */
  .band-edge  { stroke: black; stroke-width: 2; stroke-dasharray: 4 4; }
  .band-label {
    font-family: "DM Sans", system-ui, sans-serif; font-size: 13px; font-weight: 700; fill: #182420;
    paint-order: stroke; stroke: #fff; stroke-width: 4px; stroke-linejoin: round;
  }
</style>
