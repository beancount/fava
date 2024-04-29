<script lang="ts" context="module">
  import { _, format } from "../i18n";
  import type { KeySpec } from "../keyboard-shortcuts";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { journalShow } from "../stores/journal";

  const toggleText = _("Toggle %(type)s entries");

  /**
   * This is the list of all toggle buttons to show.
   * For some entry types we have subtypes (like 'cleared' for 'transaction'),
   * which get special-cased in the toggle logic below.
   */
  const buttons: [
    type: string,
    button_text: string,
    title: string | null,
    shortcut: KeySpec,
    supertype?: string,
  ][] = [
    ["open", "Open", null, "s o"],
    ["close", "Close", null, "s c"],
    ["transaction", "Transaction", null, "s t"],
    ["cleared", "*", _("Cleared transactions"), "t c", "transaction"],
    ["pending", "!", _("Pending transactions"), "t p", "transaction"],
    ["other", "x", _("Other transactions"), "t o", "transaction"],
    ["balance", "Balance", null, "s b"],
    ["note", "Note", null, "s n"],
    ["document", "Document", null, "s d"],
    [
      "discovered",
      "D",
      _("Documents with a #discovered tag"),
      "d d",
      "document",
    ],
    ["linked", "L", _("Documents with a #linked tag"), "d l", "document"],
    ["pad", "Pad", null, "s p"],
    ["query", "Query", null, "s q"],
    ["custom", "Custom", null, "s C"],
    ["budget", "B", _("Budget entries"), "s B", "custom"],
    ["metadata", _("Metadata"), _("Toggle metadata"), "m"],
    ["postings", _("Postings"), _("Toggle postings"), "p"],
  ];
</script>

<script lang="ts">
  $: shownSet = new Set($journalShow);

  function toggle(type: string) {
    journalShow.update((show) => {
      const set = new Set(show);
      const toggle_func = set.has(type)
        ? set.delete.bind(set)
        : set.add.bind(set);
      toggle_func(type);
      // Also toggle all entries that have `type` as their supertype.
      buttons.filter((b) => b[4] === type).forEach((b) => toggle_func(b[0]));
      return [...set].sort();
    });
  }

  $: active = (type: string, supertype?: string): boolean =>
    supertype != null
      ? shownSet.has(type) && shownSet.has(supertype)
      : shownSet.has(type);
</script>

<form class="flex-row">
  {#each buttons as [type, button_text, title, shortcut, supertype]}
    <button
      type="button"
      title={title ?? format(toggleText, { type: button_text })}
      use:keyboardShortcut={shortcut}
      class:inactive={!active(type, supertype)}
      on:click={() => {
        toggle(type);
      }}
    >
      {button_text}
    </button>
  {/each}
</form>

<style>
  form {
    justify-content: flex-end;
  }
</style>
