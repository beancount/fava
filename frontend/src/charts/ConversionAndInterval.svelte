<script>
  import { _ } from "../i18n";
  import { conversion, interval } from "../stores";
  import { conversions } from "../stores/chart";

  const intervals = [
    ["year", _("Yearly")],
    ["quarter", _("Quarterly")],
    ["month", _("Monthly")],
    ["week", _("Weekly")],
    ["day", _("Daily")],
  ];
</script>

<select bind:value={$conversion}>
  {#each $conversions as [conversion, conversionName]}
    <option value={conversion}>{conversionName}</option>
  {/each}
</select>
<select bind:value={$interval}>
  {#each intervals as [interval, name]}
    <option value={interval}>{name}</option>
  {/each}
</select>
