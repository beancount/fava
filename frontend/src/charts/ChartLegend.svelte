<script lang="ts">
  import { chartToggledCurrencies } from "../stores/chart";

  export let legend: [string, string][];
</script>

{#each legend as [item, color]}
  {@const isActive = !$chartToggledCurrencies.includes(item)}
  <button
    type="button"
    on:click={() => {
      if (isActive) {
        $chartToggledCurrencies = [...$chartToggledCurrencies, item];
      } else {
        $chartToggledCurrencies = $chartToggledCurrencies.filter(
          (i) => i !== item
        );
      }
    }}
    class:inactive={!isActive}
  >
    <i style="background-color: {color}" />
    <span>{item}</span>
  </button>
{/each}

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
</style>
