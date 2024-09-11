<script lang="ts">
  import type { Writable } from "svelte/store";

  /** The chart legend to show. */
  export let legend: [string, string | null][];
  /** A list of elements that are toggled. */
  export let toggled: Writable<string[]> | null = null;
  /** Alternatively, a single active element, all others are toggled. */
  export let active: Writable<string | null> | null = null;
</script>

<div>
  {#each legend as [item, color]}
    <button
      type="button"
      on:click={() => {
        if (active) {
          active.set(item);
        } else if (toggled) {
          toggled.update((v) =>
            v.includes(item) ? v.filter((i) => i !== item) : [...v, item],
          );
        }
      }}
      class:inactive={active ? item !== $active : $toggled?.includes(item)}
    >
      <i style="background-color: {color ?? '#bbb'}" />
      <span>{item}</span>
    </button>
  {/each}
</div>

<style>
  button {
    display: contents;
    color: inherit;
  }

  .inactive span {
    text-decoration: line-through;
  }

  i {
    display: inline-block;
    width: 10px;
    height: 10px;
    margin-left: 5px;
    border-radius: 10px;
  }

  .inactive i {
    filter: grayscale();
  }

  @media print {
    .inactive {
      display: none;
    }
  }
</style>
