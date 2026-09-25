<!--
  @component
  A chart legend, allowing toggling of items.
-->
<script lang="ts">
  import type { Writable } from "svelte/store";

<<<<<<< Updated upstream
  import { currencies_scale } from "./helpers.ts";
=======
  import { timedclick } from "./timedclick.ts";

  import { currenciesScale } from "./helpers.ts";
>>>>>>> Stashed changes

  interface Props {
    /** The chart legend to show. */
    legend: readonly string[];
    /** Whether to use currency colors. */
    color: boolean;
    /** A list of elements that are toggled. */
    toggled?: Writable<string[]>;
    /** Alternatively, a single active element, all others are toggled. */
    active?: Writable<string | null>;
  }

  let { legend, color, toggled, active }: Props = $props();
</script>

<div>
  {#each legend as item (item)}
    <button
      type="button"
      {@attach timedclick()}
      ontimedclick={(e) => {
        if (active) {
          active.set(item);
        } else if (toggled) {
          if (e.detail.isLong) {
            // Long press: toggle between: THIS on | ALL on
            toggled.update((v) =>
              v.length === legend.length - !v.includes(item)
                ? []
                : legend.filter((i) => i !== item),
            );
          } else {
            // Short press: toggle single button
            toggled.update((v) =>
              v.includes(item) ? v.filter((i) => i !== item) : [...v, item],
            );
          }
        }
      }}
      class:inactive={active ? item !== $active : $toggled?.includes(item)}
    >
      <i style="background-color: {color ? $currencies_scale(item) : '#bbb'}"
      ></i>
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
