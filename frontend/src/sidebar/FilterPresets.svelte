<script lang="ts">
  import { ledgerData } from "../stores";
  import AdvancedFilterPresetLink from "./AdvancedFilterPresetLink.svelte";
  import TimeFilterPresetLink from "./TimeFilterPresetLink.svelte";

  let filter_presets = $derived($ledgerData.filter_presets);
  let time_presets = $derived(
    filter_presets.filter(([type]) => type === "time"),
  );
  let advanced_presets = $derived(
    filter_presets.filter(([type]) => type === "advanced"),
  );
</script>

<div class="filter-presets">
  <div class="filter-group">
    <span class="filter-presets-label">🕒</span>
    <!-- eslint-disable-next-line @typescript-eslint/no-unused-vars -->
    {#each time_presets as [_, value, label], index}
      {#if index > 0}
        <span class="separator">·</span>
      {/if}
      <TimeFilterPresetLink {value} {label} />
    {/each}
  </div>

  <div class="filter-group">
    <span class="filter-presets-label">🎚</span>
    <!-- eslint-disable-next-line @typescript-eslint/no-unused-vars -->
    {#each advanced_presets as [_, value, label], index}
      {#if index > 0}
        <span class="separator">·</span>
      {/if}
      <AdvancedFilterPresetLink {value} {label} />
    {/each}
  </div>
</div>

<style>
  .filter-presets {
    display: flex;
    justify-content: space-between;
    width: 100%;
    padding-top: 0.5rem;
    padding-right: 0.5rem;
    padding-left: 0.5rem;

    /* background-color: var(--header-placeholder-background); */
    border-top: 1px dotted var(--header-placeholder-background);
  }

  .filter-group {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }
</style>
