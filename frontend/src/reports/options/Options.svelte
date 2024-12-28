<script lang="ts">
  import { urlFor } from "../../helpers";
  import { _ } from "../../i18n";
  import OptionsTable from "./OptionsTable.svelte";

  export let fava_options: Record<string, string>;
  export let beancount_options: Record<string, string>;
</script>

<h2>
  {_("Fava options")}
  <a href={$urlFor("help/options")}>({_("help")})</a>
</h2>
<OptionsTable options={fava_options} />

<h2>{_("Beancount options")}</h2>
<OptionsTable options={beancount_options} />
