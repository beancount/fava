<script lang="ts">
  import { filter_params, fql_filter } from "../stores/filters";

  interface Props {
    value: string;
    label: string;
  }

  let { value, label }: Props = $props();

  // Track if the filter is active (present in the current filter as a substring)
  let isActive = $derived($filter_params.filter.includes(value));

  function setAdvancedFilter() {
    const currentFilter = $filter_params.filter;

    // Check if the value is already a substring of the current filter
    if (currentFilter.includes(value)) {
      // If it's already in the filter, remove it
      const newFilter = currentFilter.replace(value, "").trim();

      fql_filter.set(newFilter);
    } else {
      // If it's not in the filter, append it
      // If the current filter is empty, just set the value
      if (!currentFilter) {
        fql_filter.set(value);
      } else {
        // Otherwise, append space-separated value
        fql_filter.set(`${currentFilter} ${value}`);
      }
    }
  }
</script>

<a href="#adv" onclick={setAdvancedFilter} class:active={isActive}>{label}</a>

<style>
  a:link {
    color: #66c4ff;
  }

  a:link:hover {
    color: #737373;
  }

  a.active {
    font-weight: bold;
    text-decoration: underline;
  }
</style>
