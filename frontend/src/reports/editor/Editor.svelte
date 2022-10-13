<script lang="ts">
  import { onMount } from "svelte";

  import { get } from "../../api";
  import router, { should_reload } from "../../router";

  import SourceEditor from "./SourceEditor.svelte";

  let filename = "";

  onMount(() =>
    router.on("page-loaded", () => {
      filename =
        new URL(window.location.href).searchParams.get("file_path") ?? "";
    })
  );

  $: load = get("source", { filename }, $should_reload);
</script>

{#await load then data}
  <SourceEditor {data} />
{/await}
