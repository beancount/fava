<script lang="ts">
  import type { Entry } from "../../entries/index.ts";
  import EntrySvelte from "../../entry-forms/Entry.svelte";
  import { _ } from "../../i18n.ts";

  interface Props {
    entry: Entry;
  }

  let { entry = $bindable() }: Props = $props();

  let duplicate = $derived(entry.is_duplicate());
  let summary = $derived(entry.summary());
</script>

<details open={!duplicate}>
  <summary class="flex-row">
    <span>
      {entry.date}{summary ? ` - ${summary}` : ""}
    </span>
    <label class="button muted">
      <input
        type="checkbox"
        checked={duplicate}
        onclick={() => {
          entry = entry.set_meta("__duplicate__", !duplicate);
        }}
      />
      {_("ignore duplicate")}
    </label>
  </summary>
  <div>
    <fieldset disabled={duplicate}>
      <EntrySvelte bind:entry {duplicate} />
    </fieldset>
  </div>
  {#if entry.meta.get("__source__")}
    <div>
      <h4>
        {_("Source")}
        {#if entry.meta.lineno}({_("Line")}: {entry.meta.lineno}){/if}
      </h4>
      <pre>{entry.meta.get("__source__")}</pre>
    </div>
  {/if}
</details>

<style>
  fieldset {
    display: contents;
  }

  details {
    /* Override the global minimum width, which would overflow the
       full-screen modal on narrow screens. */
    min-width: 0;

    summary span {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  pre {
    margin: 0;
    font-size: 0.9em;
    white-space: pre-wrap;
  }
</style>
