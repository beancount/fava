<script lang="ts">
  import { _, format } from "../i18n";
  import { getInterval, intervalLabel, INTERVALS } from "../lib/interval";
  import { conversion, interval } from "../stores";
  import { conversions } from "../stores/chart";
  import SelectCombobox from "./SelectCombobox.svelte";

  const conversion_description = (option: string) => {
    switch (option) {
      case "at_cost":
        return _("At Cost");
      case "at_value":
        return _("At Market Value");
      case "units":
        return _("Units");
      default:
        return format(_("Converted to %(currency)s"), { currency: option });
    }
  };

  const is_currency_conversion = (option: string) =>
    !["at_cost", "at_value", "units"].includes(option);
</script>

<SelectCombobox
  bind:value={$conversion}
  options={$conversions}
  description={conversion_description}
  multiple_select={is_currency_conversion}
/>

<SelectCombobox
  bind:value={$interval}
  options={INTERVALS}
  description={(o) => intervalLabel(getInterval(o))}
/>
