<script lang="ts">
  import { get_context, get_source_slice } from "../api/index.ts";
  import SliceEditor from "../editor/SliceEditor.svelte";
  import { _ } from "../i18n.ts";
  import ReportLoadError from "../reports/ReportLoadError.svelte";
  import { hash } from "../stores/url.ts";
  import EntryContextBalances from "./EntryContextBalances.svelte";
  import EntryContextLocation from "./EntryContextLocation.svelte";
  import ModalBase from "./ModalBase.svelte";

  let shown = $derived($hash.startsWith("context"));
  let entry_hash = $derived(shown ? $hash.slice(8) : "");
</script>

<ModalBase {shown}>
  <div class="content">
    {#if shown}
      {#await get_context({ entry_hash })}
        <p>Loading entry context...</p>
      {:then { entry, balances_after, balances_before }}
        <EntryContextLocation {entry} />
        {#if balances_before}
          <EntryContextBalances {balances_before} {balances_after} />
        {/if}
        {#if entry.meta.lineno !== "0" && !entry.meta.filename.startsWith("<")}
          {#await Promise.all( [get_source_slice( { entry_hash }, ), import("../codemirror/beancount.ts")], )}
            <p>Loading entry slice...</p>
          {:then [{ slice, sha256sum }, codemirror_beancount]}
            <SliceEditor
              {entry_hash}
              {slice}
              {sha256sum}
              {codemirror_beancount}
            />
          {:catch error}
            <ReportLoadError title={_("Context")} {error} />
          {/await}
        {/if}
      {:catch error}
        <ReportLoadError title={_("Context")} {error} />
      {/await}
    {/if}
  </div>
</ModalBase>
