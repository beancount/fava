<script lang="ts">
  import { filter_params, time_filter } from "../stores/filters";

  interface Props {
    value: string;
    label: string;
  }

  let { value, label }: Props = $props();

  let isActive = $derived($filter_params.time === value);

  function setTimeFilter() {
    if (isActive) {
      time_filter.set("");
    } else {
      time_filter.set(value);
    }
  }
</script>

<a href="#time" onclick={setTimeFilter} class:active={isActive}>{label}</a>

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
