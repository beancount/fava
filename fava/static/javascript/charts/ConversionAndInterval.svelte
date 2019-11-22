<script>
  import { _ } from "../helpers";
  import { conversion, interval } from "../stores";
  import { conversions } from "../stores/chart";

  const intervals = {
    year: _("Yearly"),
    quarter: _("Quarterly"),
    month: _("Monthly"),
    week: _("Weekly"),
    day: _("Daily"),
  };
</script>

<select bind:value={$conversion}>
  {#each $conversions as [conversion, conversionName]}
    <option value={conversion}>{conversionName}</option>
  {/each}
</select>
<select bind:value={$interval}>
  {#each Object.keys(intervals) as key}
    <option value={key}>{intervals[key]}</option>
  {/each}
</select>
