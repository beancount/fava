<script lang="ts">
  import type { Entry } from "../../entries/index.ts";
  import EntrySvelte from "../../entry-forms/Entry.svelte";
  import { _ } from "../../i18n.ts";
  import { keyboard_shortcut } from "../../keyboard-shortcuts.ts";
  import ModalBase from "../../modals/ModalBase.svelte";

  interface Props {
    entries: Entry[];
    save: () => void;
    close: () => void;
  }

  let { entries = $bindable(), save, close }: Props = $props();

  let count = $derived(entries.length);
  let shown = $derived(count > 0);

  let count_duplicates = $derived(
    entries.filter((e) => e.is_duplicate()).length,
  );
  let count_without_duplicates = $derived(count - count_duplicates);
</script>

<ModalBase {shown} close_handler={close}>
  <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
  <form
    class="flex-column"
    onsubmit={(event) => {
      event.preventDefault();
      save();
    }}
    onkeydown={(event) => {
      if (event.key === "Enter" && event.target instanceof HTMLInputElement) {
        // Do not submit the whole form with possibly many entries on a bare Enter.
        event.preventDefault();
        if (event.ctrlKey || event.metaKey) {
          event.currentTarget.requestSubmit();
        }
      }
    }}
    oninvalidcapture={(event) => {
      // Allow invalid fields to be focused
      if (event.target instanceof HTMLElement) {
        const details = event.target.closest("details");
        if (details) {
          details.open = true;
        }
      }
    }}
  >
    <h3>
      {_("Import")}
      {count} ({count_without_duplicates}
      to import)
    </h3>
    <div class="entries">
      {#each entries as entry, index (index)}
        {@const duplicate = entry.is_duplicate()}
        {@const summary = entry.summary()}
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
                  entries[index] = entry.set_meta(
                    "__duplicate__",
                    !entry.is_duplicate(),
                  );
                }}
              />
              {_("ignore duplicate")}
            </label>
          </summary>
          <div>
            <fieldset disabled={duplicate}>
              <EntrySvelte
                bind:entry={
                  () => entry,
                  (entry: Entry) => {
                    entries[index] = entry;
                  }
                }
                {duplicate}
              />
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
      {/each}
    </div>
    <div class="flex-row">
      <span class="spacer"></span>
      <button
        type="submit"
        {@attach keyboard_shortcut({ key: "Control+Enter", mac: "Meta+Enter" })}
      >
        {_("Save")}
      </button>
    </div>
  </form>
</ModalBase>

<style>
  fieldset {
    display: contents;
  }

  form {
    max-height: calc(90vh - 2em);
  }

  @media (width <= 767px) {
    /* The modal is shown full-screen on mobile. */
    form {
      max-height: 100%;
    }
  }

  .entries {
    overflow: auto;
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
