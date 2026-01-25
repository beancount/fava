<script lang="ts" generics="T extends string">
  import type { LocalStoreSyncedStore } from "../lib/store.ts";

  interface Props {
    /** The store to show a switch for. */
    store: LocalStoreSyncedStore<T>;
    /** URL value that overrides the store value when set. */
    url_value?: T | null;
    /** Callback when the value changes. */
    onchange?: (value: T) => void;
  }

  let { store, url_value, onchange }: Props = $props();

  // URL value takes precedence over store value if it's a valid option
  let effective_value = $derived.by(() => {
    const valid_options = store.values().map(([opt]) => opt);
    if (url_value != null && valid_options.includes(url_value)) {
      return url_value;
    }
    return $store;
  });

  function handle_change(option: T) {
    store.set(option);
    onchange?.(option);
  }
</script>

<span>
  {#each store.values() as [option, name] (option)}
    <label class="button" class:muted={effective_value !== option}>
      <input
        type="radio"
        checked={effective_value === option}
        value={option}
        onchange={() => {
          handle_change(option);
        }}
      />
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
