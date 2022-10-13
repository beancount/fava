<script lang="ts">
  import { get } from "../../api";
  import { should_reload } from "../../router";
  import { filter_params } from "../../stores/filters";

  import Documents from "./Documents.svelte";

  $: load = get("documents", $filter_params, $should_reload);
</script>

{#await load then documents}
  <Documents data={documents} />
{/await}
