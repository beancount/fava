<script lang="ts">
  import type { Note } from "../entries";
  import { _ } from "../i18n";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";

  export let entry: Note;
</script>

<div>
  <div class="flex-row">
    <input type="date" name="date" bind:value={entry.date} required />
    <h4>{_("Note")}</h4>
    <AccountInput
      className="grow"
      bind:value={entry.account}
      date={entry.date}
    />
    <AddMetadataButton bind:meta={entry.meta} />
  </div>
  <textarea name="comment" rows={2} bind:value={entry.comment}></textarea>
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
