<script>
  /** LayerCake <Svg> child: dollar gridlines + labels, plus the dashed $100k callout. */
  import { getContext } from "svelte";
  import { format } from "d3-format";

  export let ticks = [];
  export let refValue = 100000;

  const { yScale, width } = getContext("LayerCake");
  const comma = format(",");
  const tickLabel = (v, i) => (v === 0 ? "" : i === ticks.length - 1 ? "$" + comma(v) : comma(v));

  $: ry = $yScale(refValue); // dashed $100k line position
</script>

<g class="axis">
  <!-- spine + baseline -->
  <line class="spine" x1="0" x2="0" y1="0" y2={$yScale(0)} />
  <line class="spine" x1="0" x2={$width} y1={$yScale(0)} y2={$yScale(0)} />

  {#each ticks as v, i}
    {@const y = $yScale(v)}
    {#if v !== 0 && v !== refValue}
      <line class="grid" x1="0" x2={$width} y1={y} y2={y} />
    {/if}
    <text class="ytick" x="-10" y={y} dy=".32em" text-anchor="end">{tickLabel(v, i)}</text>
  {/each}

  <line class="refline" x1="0" x2={$width} y1={ry} y2={ry} />
  <text class="reftag" x={$width} y={ry - 8} text-anchor="end">$100,000 cost of attendance</text>
</g>

<style>
  .grid    { stroke: #eef2f0; stroke-width: 1; }
  .spine   { stroke: #e6ebe8; stroke-width: 1; }
  .refline { stroke: #62706a; stroke-width: 1; stroke-dasharray: 4 4; }
  .ytick   { font-family: "DM Sans", system-ui, sans-serif; font-size: 12px; fill: #62706a; font-weight: 500; }
  .reftag  { font-family: "DM Sans", system-ui, sans-serif; font-size: 12px; fill: #182420; font-weight: 800; }
</style>
