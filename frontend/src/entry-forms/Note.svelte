<script lang="ts">
  import type { EntryMetadata, Note } from "../entries";
  import { _ } from "../i18n";
  import AccountInput from "./AccountInput.svelte";
  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadataSvelte from "./EntryMetadata.svelte";

  interface Props {
    entry: Note;
  }

  let { entry = $bindable() }: Props = $props();
</script>

<div>
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
      className="grow"
      bind:value={
        () => entry.account,
        (account: string) => {
          entry = entry.set("account", account);
        }
      }
      date={entry.date}
      required
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
    name="comment"
    rows={2}
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
    flex-grow: 1;
    width: 100%;
    padding: 8px;
    font: inherit;
  }
</style>
