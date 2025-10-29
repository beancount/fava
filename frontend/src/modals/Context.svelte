<script lang="ts">
  import { get_context } from "../api/index.ts";
  import { getBeancountLanguageSupport } from "../codemirror/beancount.ts";
  import SliceEditor from "../editor/SliceEditor.svelte";
  import { _ } from "../i18n.ts";
  import ReportLoadError from "../reports/ReportLoadError.svelte";
  import { hash } from "../stores/url.ts";
  import EntryContext from "./EntryContext.svelte";
  import ModalBase from "./ModalBase.svelte";

  let shown = $derived($hash.startsWith("context"));
  let entry_hash = $derived(shown ? $hash.slice(8) : "");
  let content = $derived(shown ? get_context({ entry_hash }) : null);
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
    {:catch error}
      <ReportLoadError title={_("Context")} {error} />
    {/await}
  </div>
</ModalBase>
