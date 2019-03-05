<script>
  import { _ } from "../helpers";

  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";

  export let entry;
</script>
<div class="entry-form">
  <div class="fieldset">
    <input type="date" name="date" bind:value="{entry.date}" required />
    <h4>{_('Note')}</h4>
    <AccountInput bind:value="{entry.account}" />
    <AddMetadataButton bind:meta="{entry.meta}" />
  </div>
  <div class="fieldset">
    <textarea name="comment" rows="2" bind:value="{entry.comment}"></textarea>
  </div>
  <EntryMetadata bind:meta="{entry.meta}" />
</div>
