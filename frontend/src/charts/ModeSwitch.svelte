<script lang="ts" generics="T extends string">
  import type { LocalStoreSyncedStore } from "../lib/store";

  /** The store to show a switch for. */
  export let store: LocalStoreSyncedStore<T>;
</script>

<span>
  {#each store.values() as [option, name]}
    <label class="button" class:muted={$store !== option}>
      <input type="radio" bind:group={$store} value={option} />
      {name}
    </label>
  {/each}
</span>

<style>
  input {
    display: none;
  }

  label + label {
    margin-left: 0.125rem;
  }

  @media print {
    label {
      display: none;
    }
  }
</style>
