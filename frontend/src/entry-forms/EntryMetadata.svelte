<script lang="ts">
  import type { EntryMetadata } from "../entries";
  import { _ } from "../i18n";
  import { metaValueToString, stringToMetaValue } from "./metadata";

  export let meta: EntryMetadata;

  $: metakeys = Object.keys(meta).filter(
    (key) => !key.startsWith("_") && key !== "filename" && key !== "lineno",
  );

  function removeMetadata(metakey: string) {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { [metakey]: ignored, ...rest } = meta;
    meta = rest;
  }

  function updateMetakey(currentKey: string, newKey: string) {
    meta = Object.keys(meta).reduce<EntryMetadata>((m, key) => {
      if (key === currentKey) {
        const val = meta[currentKey];
        if (val !== undefined) {
          m[newKey] = val;
        }
      } else {
        const val = meta[key];
        if (val != null) {
          m[key] = val;
        }
      }
      return m;
    }, {});
  }

  function addMetadata() {
    meta[""] = "";
    meta = meta;
  }
</script>

{#each metakeys as metakey, i}
  <div class="flex-row">
    <button
      type="button"
      class="muted round remove-row"
      on:click={() => {
        removeMetadata(metakey);
      }}
      tabindex={-1}
    >
      ×
    </button>
    <input
      type="text"
      class="key"
      placeholder={_("Key")}
      value={metakey}
      on:change={(event) => {
        updateMetakey(metakey, event.currentTarget.value);
      }}
      required
    />
    <input
      type="text"
      class="value"
      placeholder={_("Value")}
      value={metaValueToString(meta[metakey] ?? "")}
      on:change={(event) => {
        meta[metakey] = stringToMetaValue(event.currentTarget.value);
      }}
    />
    {#if i === metakeys.length - 1}
      <button
        type="button"
        class="muted round"
        on:click={addMetadata}
        title={_("Add metadata")}
      >
        +
      </button>
    {/if}
  </div>
{/each}

<style>
  div {
    padding-left: 56px;
    font-size: 0.8em;
  }

  input.key {
    width: 10em;
  }

  input.value {
    flex-grow: 1;
    max-width: 15em;
  }

  @media (width <= 767px) {
    div {
      padding-left: 0;
    }
  }
</style>
