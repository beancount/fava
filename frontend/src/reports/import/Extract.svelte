<script lang="ts">
  import { untrack } from "svelte";

  import type { Entry } from "../../entries/index.ts";
  import { _, format } from "../../i18n.ts";
  import { keyboard_shortcut } from "../../keyboard-shortcuts.ts";
  import { log_error } from "../../log.ts";
  import ModalBase from "../../modals/ModalBase.svelte";
  import { import_grouping } from "../../stores/import.ts";
  import ExtractEntry from "./ExtractEntry.svelte";
  import { group_entries } from "./group.ts";

  interface Props {
    entries: Entry[];
    save: () => void;
    save_group: (indices: number[]) => Promise<void>;
    close: () => void;
  }

  let { entries = $bindable(), save, save_group, close }: Props = $props();

  let shown = $derived(entries.length > 0);

  /** The grouping of the entries in their current state. */
  let current_groups = $derived(group_entries(entries, $import_grouping));
  // Only regroup automatically when the grouping or the list of entries is
  // changed and not on edits, which would move the entry that is being edited.
  let groups = $derived.by(() => {
    const current = entries;
    const grouping = $import_grouping;
    return untrack(() => group_entries(current, grouping));
  });
  let groups_outdated = $derived(
    JSON.stringify(groups) !== JSON.stringify(current_groups),
  );

  /** Save the entries of the group if all its fields are valid. */
  function validate_and_save_group(
    details: HTMLDetailsElement,
    indices: number[],
  ) {
    const fields = details.querySelectorAll<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >("input, select, textarea");
    if ([...fields].every((field) => field.reportValidity())) {
      save_group(indices).catch(log_error);
    }
  }
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
        let details = event.target.closest("details");
        while (details) {
          details.open = true;
          details = details.parentElement?.closest("details") ?? null;
        }
      }
    }}
  >
    <div class="flex-row header">
      <h3>{_("Import")}</h3>
      <span class="spacer"></span>
      <label>
        <span>{_("Group by")}:</span>
        <select bind:value={$import_grouping}>
          <option value="status">{_("Status")}</option>
          <option value="accounts">{_("Accounts")}</option>
          <option value="payee">{_("Payee")}</option>
        </select>
      </label>
      {#if groups_outdated}
        <button
          type="button"
          class="muted"
          onclick={() => {
            groups = current_groups;
          }}
        >
          {_("Regroup")}
        </button>
      {/if}
    </div>
    <div class="entries">
      {#each groups as [label, indices] (label)}
        {@const to_import = indices.filter(
          (index) => entries[index]?.is_duplicate() === false,
        )}
        <details class="group" open>
          <summary class="flex-row">
            <span>{label}</span>
            <span class="spacer"></span>
            <span>
              {format(_("%(count)s (%(to_import)s to import)"), {
                count: indices.length.toString(),
                to_import: to_import.length.toString(),
              })}
            </span>
            <button
              type="button"
              class="muted"
              onclick={(event) => {
                const details = event.currentTarget.closest("details");
                if (details) {
                  validate_and_save_group(details, indices);
                }
              }}
            >
              {_("Save")}
            </button>
          </summary>
          <div>
            {#each indices as index (index)}
              {@const entry = entries[index]}
              {#if entry}
                <ExtractEntry
                  bind:entry={
                    () => entry,
                    (entry: Entry) => {
                      entries[index] = entry;
                    }
                  }
                />
              {/if}
            {/each}
          </div>
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
  form {
    max-height: calc(90vh - 2em);
  }

  @media (width <= 767px) {
    /* The modal is shown full-screen on mobile. */
    form {
      max-height: 100%;
    }
  }

  .header {
    padding-right: 2.5em;
  }

  .entries {
    overflow: auto;
  }

  details {
    /* Override the global minimum width, which would overflow the
       full-screen modal on narrow screens. */
    min-width: 0;
  }

  .group > summary {
    font-weight: 500;
    background-color: var(--summary-background-darker);
  }
</style>
