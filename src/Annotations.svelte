<script>
  /**
   * LayerCake <Svg> child: arrow annotations for individual bars.
   * Anchor is chosen by zone so labels extend away from the chart centre and never
   * collide: left-edge bars read rightward, right-edge bars leftward, the rest are
   * centred over their own bar. Labels clamp below the top edge; a white halo keeps
   * them legible over bars.
   */
  import { getContext } from "svelte";
  import { format } from "d3-format";

  export let items = []; // [{ i, title }]


  const { data, xScale, yScale, width } = getContext("LayerCake");
  const money = format("$,");

  const RISE = 54; // vertical distance from bar top up to the label
  const GAP = 8;   // gap between arrow tip and bar top
  $: bw = $xScale.bandwidth();
</script>

<defs>
  <marker id="ann-arrow" markerWidth="9" markerHeight="9" refX="6.5" refY="3" orient="auto">
    <path d="M0,0 L6.5,3 L0,6 Z" fill="#182420" />
  </marker>
</defs>

{#each items as a (a.i)}
  {@const d = $data[a.i]}
  {@const cx = $xScale(a.i) + bw / 2}
  {@const topY = $yScale(d.net)}
  {@const zone = cx < $width * 0.15 ? "start" : cx > $width * 0.85 ? "end" : "middle"}
  {@const labelX = zone === "start" ? cx + 2 : zone === "end" ? cx - 2 : cx}
  {@const labelY = Math.max(topY - RISE, 16)}

  <g class="ann">
    <line x1={labelX} y1={labelY + 25} x2={cx} y2={topY - GAP} marker-end="url(#ann-arrow)" />
    <text x={labelX} y={labelY} text-anchor={zone}>
      <tspan class="nm" x={labelX}>{a.title}</tspan>
      <tspan class="v" x={labelX} dy="1.25em">{money(d.net)} after aid</tspan>
    </text>
  </g>
{/each}

<style>
  .ann line { stroke: #182420; stroke-width: 1.25; }
  .ann text {
    font-family: "DM Sans", system-ui, sans-serif;
    paint-order: stroke; stroke: #fff; stroke-width: 3.5px; stroke-linejoin: round;
  }
  .ann .nm { font-weight: 700; font-size: 15px; fill: #182420; }
  .ann .v  { font-weight: 600; font-size: 13px; fill: #3a4a44; }
</style>
