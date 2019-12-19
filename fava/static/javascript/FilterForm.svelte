<script>
  import { _ } from "./helpers";
  import { filters as filterStore, favaAPI } from "./stores";
  import AutocompleteInput from "./AutocompleteInput.svelte";

  const filters = [
    {
      name: "time",
      placeholder: _("Time"),
      key: "f t",
      suggestions: favaAPI.years,
    },
    {
      name: "account",
      placeholder: _("Account"),
      key: "f a",
      suggestions: favaAPI.accounts,
    },
    {
      name: "filter",
      placeholder: _("Filter by tag, payee, ..."),
      key: "f f",
      suggestions: [
        ...favaAPI.tags.map(tag => `#${tag}`),
        ...favaAPI.links.map(link => `^${link}`),
        ...favaAPI.payees.map(payee => `payee:"${payee}"`),
      ],
      autocompleteOptions: {
        valueExtractor(value, input) {
          const [ret] = value.slice(0, input.selectionStart).match(/\S*$/);
          return ret;
        },
        valueSelector(value, input) {
          const [search] = input.value
            .slice(0, input.selectionStart)
            .match(/\S*$/);
          return `${input.value.slice(
            0,
            input.selectionStart - search.length
          )}${value}${input.value.slice(input.selectionStart)}`;
        },
      },
    },
  ];

  let values;
  filterStore.subscribe(fs => {
    values = { ...fs };
  });

  function submit() {
    filterStore.update(fs => {
      Object.assign(fs, values);
      return fs;
    });
  }

  function clear(name) {
    filterStore.update(fs => {
      const ret = { ...fs };
      ret[name] = "";
      return ret;
    });
  }
</script>

<form id="filter-form" class="filter-form" on:submit|preventDefault={submit}>
  {#each filters as { name, placeholder, key, suggestions, autocompleteOptions }}
    <span class:empty={!values[name]}>
      <AutocompleteInput
        bind:value={values[name]}
        {placeholder}
        {suggestions}
        setSize={true}
        {...autocompleteOptions}
        on:select={submit} />
      <button
        type="button"
        tabindex="-1"
        class="close muted round"
        on:click={() => clear(name)}>
        ×
      </button>
    </span>
  {/each}
  <button type="submit" />
</form>
