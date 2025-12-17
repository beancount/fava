<script lang="ts">
  import type { EntryMetadata } from "../entries/index.ts";
  import { _ } from "../i18n.ts";

  interface Props {
    meta: EntryMetadata;
  }

  let { meta = $bindable() }: Props = $props();

  let meta_entries = $derived(meta.entries());
</script>

{#each meta_entries as [key, value], index (index)}
  <div class="flex-row">
    <button
      type="button"
      class="muted round remove-row"
      onclick={() => {
        meta = meta.delete(key);
      }}
      tabindex={-1}
    >
      ×
    </button>
    <input
      type="text"
      class="key"
      placeholder={_("Key")}
      value={key}
      onchange={(event) => {
        meta = meta.update_key(key, event.currentTarget.value);
      }}
      required
    />
    :
    <input
      type="text"
      class="value"
      placeholder={_("Value")}
      {value}
      onchange={(event) => {
        meta = meta.set_string(key, event.currentTarget.value);
      }}
    />
    {#if index === meta_entries.length - 1 && key}
      <button
        type="button"
        class="muted round"
        onclick={() => {
          meta = meta.add();
        }}
        aria-label={_("Add metadata")}
        title={_("Add metadata")}
      >
        +
      </button>
    {/if}
  </div>
{/each}

<style>
  div {
    padding-left: 3rem;
  }

  input.key {
    width: 12rem;
  }

  input.value {
    flex-grow: 1;
  }

  @media (width <= 767px) {
    div {
      padding-left: 0;
    }
  }
</style>
