<script lang="ts">
  import { get } from "../../api";
  import { should_reload } from "../../router";

  import { preprocessData } from "./helpers";
  import Import from "./Import.svelte";

  $: load = get("imports", undefined, $should_reload).then(preprocessData);
</script>

{#await load then documents}
  <Import data={documents} />
{/await}

<!-- 
{% if not ledger.fava_options.import_config %}
<p>
No importers configured. See <a href="{{ url_for('help_page', page_slug='import') }}">Help (Import)</a> for more information.
</p>
{% else %}
<svelte-component type="import"><script type="application/json">{{ ledger.ingest.import_data()|tojson }}</script></svelte-component>
{% endif %} -->
