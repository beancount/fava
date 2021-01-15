<script>
  import { _ } from "../i18n";

  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";

  /** @type {import("../entries").Note} */
  export let entry;
</script>

<div>
  <div class="flex-row">
    <input type="date" name="date" bind:value={entry.date} required />
    <h4>{_("Note")}</h4>
    <AccountInput className="grow" bind:value={entry.account} />
    <AddMetadataButton bind:meta={entry.meta} />
  </div>
  <textarea name="comment" rows={2} bind:value={entry.comment} />
  <EntryMetadata bind:meta={entry.meta} />
</div>

<style>
  textarea {
    flex-grow: 1;
    width: 100%;
    padding: 8px;
    font: inherit;
  }
</style>
