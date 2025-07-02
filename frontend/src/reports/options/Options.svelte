<script lang="ts">
  import ModeSwitch from "../../charts/ModeSwitch.svelte";
  import { urlFor } from "../../helpers";
  import { _ } from "../../i18n";
  import { color_scheme } from "../../stores/color_scheme";
  import type { OptionsReportProps } from ".";
  import OptionsTable from "./OptionsTable.svelte";

  let { fava_options, beancount_options }: OptionsReportProps = $props();
</script>

<h2>
  {_("Color scheme")}
</h2>
<p>
  <ModeSwitch store={color_scheme} />
</p>

<h2>
  {_("Fava options")}
  <a href={$urlFor("help/options")}>({_("help")})</a>
</h2>
<OptionsTable options={fava_options} />

<h2>{_("Beancount options")}</h2>
<OptionsTable options={beancount_options} />
