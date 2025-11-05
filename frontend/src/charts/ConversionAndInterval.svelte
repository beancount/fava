<script lang="ts">
  import { _, format } from "../i18n.ts";
  import {
    DEFAULT_INTERVAL,
    getInterval,
    intervalLabel,
    INTERVALS,
  } from "../lib/interval.ts";
  import { router } from "../router.ts";
  import { conversions } from "../stores/chart.ts";
  import { conversion, interval } from "../stores/url.ts";
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
  bind:value={
    () => $conversion,
    (value: string) => {
      router.set_search_param("conversion", value === "at_cost" ? "" : value);
    }
  }
  options={$conversions}
  description={conversion_description}
  multiple_select={is_currency_conversion}
/>

<SelectCombobox
  bind:value={
    () => $interval,
    (value: string) => {
      router.set_search_param(
        "interval",
        value === DEFAULT_INTERVAL ? "" : value,
      );
    }
  }
  options={INTERVALS}
  description={(o: string) => intervalLabel(getInterval(o))}
/>
