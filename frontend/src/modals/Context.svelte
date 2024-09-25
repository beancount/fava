<script lang="ts">
  import { get } from "../api";
  import { getBeancountLanguageSupport } from "../codemirror/beancount";
  import SliceEditor from "../editor/SliceEditor.svelte";
  import { urlHash } from "../stores/url";
  import EntryContext from "./EntryContext.svelte";
  import ModalBase from "./ModalBase.svelte";

  $: shown = $urlHash.startsWith("context");
  $: entry_hash = shown ? $urlHash.slice(8) : "";
  $: content = shown ? get("context", { entry_hash }) : null;
</script>

<ModalBase {shown}>
  <div class="content">
    {#await content}
      Loading entry context...
    {:then response}
      {#if response}
        <EntryContext
          entry={response.entry}
          balances_before={response.balances_before}
          balances_after={response.balances_after}
        />
        {#await getBeancountLanguageSupport() then beancount_language_support}
          <SliceEditor
            {entry_hash}
            slice={response.slice}
            sha256sum={response.sha256sum}
            {beancount_language_support}
          />
        {:catch}
          Loading tree-sitter language failed...
        {/await}
      {/if}
    {:catch}
      Loading entry context failed...
    {/await}
  </div>
</ModalBase>
