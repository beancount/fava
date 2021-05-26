<script lang="ts">
  export let x;

  export let lastDate;
  export let innerHeight;

  export let hasFutureData;

  let today = new Date();
  $: hasFutureData = lastDate > today;
</script>

{#if hasFutureData}
  <!--
    The width is extended by 2 pixels to ensure it extends past a trailing
    circle, in the case of line charts.
   -->
  <filter id="futureColorFilter" filterUnits="userSpaceOnUse">
    <feFlood
      flood-color="black"
      flood-opacity="0.6"
      x={x(today)}
      y={0}
      width={x(lastDate) - x(today) + 2}
      height={innerHeight}
      result="fill"
    />
    <feBlend in="fill" in2="SourceGraphic" mode="color" result="blend" />
    <feComposite in="blend" in2="SourceGraphic" operator="in" />
  </filter>
{/if}
