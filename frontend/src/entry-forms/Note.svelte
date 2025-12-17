<script lang="ts">
  import type { EntryMetadata, Note } from "../entries/index.ts";
  import { _ } from "../i18n.ts";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadataSvelte from "./EntryMetadata.svelte";

  interface Props {
    entry: Note;
  }

  let { entry = $bindable() }: Props = $props();
</script>

<div class="flex-column">
  <div class="flex-row">
    <input
      type="date"
      name="date"
      bind:value={
        () => entry.date,
        (date: string) => {
          entry = entry.set("date", date);
        }
      }
      required
    />
    <h4>{_("Note")}</h4>
    <AccountInput
      bind:value={
        () => entry.account,
        (account: string) => {
          entry = entry.set("account", account);
        }
      }
      date={entry.date}
      required
      --autocomplete-wrapper-flex="1"
    />
    <AddMetadataButton
      bind:meta={
        () => entry.meta,
        (meta: EntryMetadata) => {
          entry = entry.set("meta", meta);
        }
      }
    />
  </div>
  <textarea
    rows={2}
    placeholder="Comment"
    bind:value={
      () => entry.comment,
      (comment: string) => {
        entry = entry.set("comment", comment);
      }
    }
  ></textarea>
  <EntryMetadataSvelte
    bind:meta={
      () => entry.meta,
      (meta: EntryMetadata) => {
        entry = entry.set("meta", meta);
      }
    }
  />
</div>

<style>
  textarea {
    resize: vertical;
  }
</style>
