<script>
  /** LayerCake <Svg> child. Ghost = sticker (light); fill = cost after aid (dark). */
  import { getContext } from "svelte";

  export let dropped = false;     // false = bars at sticker; true = bars at net
  export let emphAll = false;     // draw every bar dark
  export let emphSet = new Set(); // indices drawn dark when emphAll is false

  const { data, xScale, yScale } = getContext("LayerCake");
  $: bw = $xScale.bandwidth();
  $: y0 = $yScale(0);
</script>

<g class="bars">
  {#each $data as d (d.i)}
    {@const x = $xScale(d.i)}
    {@const stickerY = $yScale(d.s)}
    {@const fillTopY = dropped ? $yScale(d.net) : stickerY}
    {@const emph = emphAll || emphSet.has(d.i)}

    <rect class="ghost" x={x} y={stickerY} width={bw} height={y0 - stickerY} />
    <rect class="fill" x={x} width={bw}
          style="y:{fillTopY}px;height:{y0 - fillTopY}px;opacity:{emph ? 1 : 0}" />
  {/each}
</g>

<style>
  .ghost { fill: rgba(0, 122, 88, 0.16); }
  .fill  { fill: #007a58; transition: y .32s ease-out, height .32s ease-out, opacity .32s ease-out; }
</style>
