<script>
  import { _ } from "../helpers";

  export let meta;

  $: metakeys = Object.keys(meta).filter(
    key => !key.startsWith("_") && key !== "filename" && key !== "lineno"
  );

  function removeMetadata(metakey) {
    delete meta[metakey];
    meta = meta;
  }

  function updateMetakey(currentKey, newKey) {
    meta = Object.keys(meta).reduce((m, key) => {
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
<div class="metadata">
  {#each metakeys as metakey }
  <div class="fieldset">
    <button
      class="muted round remove-fieldset"
      on:click="{() => removeMetadata(metakey)}"
      type="button"
      tabindex="-1"
    >
      ×
    </button>
    <input
      type="text"
      class="metadata-key"
      placeholder="{_('Key')}"
      value="{metakey}"
      on:change="{ (event) => { updateMetakey(metakey, event.target.value) } }"
      required
    />
    <input
      type="text"
      class="metadata-value"
      placeholder="{_('Value')}"
      bind:value="{meta[metakey]}"
    />
    <button
      class="muted round add-row"
      type="button"
      on:click="{addMetadata}"
      title="{_('Add metadata')}"
    >
      +
    </button>
  </div>
  {/each}
</div>
