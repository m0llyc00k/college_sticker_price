<script>
  import { getContext } from "svelte";
  export let show = false;
  export let stickerY = 100000; // dollar height to park the "cost of attendance" label
  export let netY = 35000;      // dollar height to park the "cost after aid" label
  const { yScale, width } = getContext("LayerCake");
</script>

{#if show}
  <g class="band-labels">
    <text class="lbl faded" x={$width / 2} y={$yScale(stickerY) + 80} text-anchor="middle">
      Cost of attendance
    </text>
    <text class="lbl solid" x={$width / 2} y={$yScale(netY) - 30} text-anchor="middle">
      Cost after aid
    </text>
  </g>
{/if}

<style>
  .lbl{
    font-family:"DM Sans", system-ui, sans-serif;
    paint-order:stroke; stroke:#fff; stroke-width:4px; stroke-linejoin:round;
    font-weight:700; font-size:16px;
  }
  .faded{ fill:#6b7772; }   /* muted, matches the ghost bars */
  .solid{ fill:#007a58; }   /* green, matches the net fill */
</style>