<script lang="ts">
  import { _ } from "../i18n";

  export let meta: Record<string, unknown>;

  $: metakeys = Object.keys(meta).filter(
    (key) => !key.startsWith("_") && key !== "filename" && key !== "lineno"
  );

  function removeMetadata(metakey: string) {
    delete meta[metakey];
    meta = meta;
  }

  function updateMetakey(currentKey: string, newKey: string) {
    meta = Object.keys(meta).reduce<Record<string, unknown>>((m, key) => {
      if (key === currentKey) {
        m[newKey] = meta[currentKey];
      } else {
        m[key] = meta[key];
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
      class="muted round remove-row"
      on:click={() => removeMetadata(metakey)}
      type="button"
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
      bind:value={meta[metakey]}
    />
    {#if i === metakeys.length - 1}
      <button
        class="muted round"
        type="button"
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

  @media (max-width: 767px) {
    div {
      padding-left: 0;
    }
  }
</style>
