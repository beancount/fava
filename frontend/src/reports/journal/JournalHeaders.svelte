<script lang="ts">
  import { _ } from "../../i18n.ts";
  import { journal_sort } from "../../stores/journal.ts";
  import type { JournalSortColumn } from "./sort.ts";

  interface Props {
    disabled: boolean;
    show_change_and_balance: boolean;
    set_sort_column: (name: JournalSortColumn) => void;
  }

  let { disabled, show_change_and_balance, set_sort_column }: Props = $props();

  let [name, order] = $derived($journal_sort);
</script>

<ol class="flex-table journal">
  <li class="head">
    <p>
      <button
        type="button"
        class="datecell unset"
        data-order={name === "date" ? order : undefined}
        {disabled}
        onclick={() => {
          set_sort_column("date");
        }}
      >
        {_("Date")}
      </button>
      <button
        type="button"
        class="flag unset"
        data-order={name === "flag" ? order : undefined}
        {disabled}
        onclick={() => {
          set_sort_column("flag");
        }}
      >
        {_("F")}
      </button>
      <button
        type="button"
        class="description unset"
        data-order={name === "narration" ? order : undefined}
        {disabled}
        onclick={() => {
          set_sort_column("narration");
        }}
      >
        {_("Payee")}/{_("Narration")}
      </button>
      <span class="num">{_("Units")}</span>
      {#if show_change_and_balance}
        <button
          type="button"
          class="num unset"
          data-order={name === "change" ? order : undefined}
          {disabled}
          onclick={() => {
            set_sort_column("change");
          }}
        >
          {_("Cost")} / {_("Change")}
        </button>
        <span class="num">{_("Price")} / {_("Balance")}</span>
      {:else}
        <span class="num">{_("Cost")}</span>
        <span class="num">{_("Price")}</span>
      {/if}
    </p>
  </li>
</ol>

<style>
  ol {
    margin: var(--flex-gap) 0 0;
  }

  button {
    position: relative;
  }

  button.num {
    padding-left: 18px;
  }

  button.num[data-order]::after {
    right: auto;
    left: 4px;
  }
</style>
