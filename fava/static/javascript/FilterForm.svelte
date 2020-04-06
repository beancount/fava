<script>
  import { _ } from "./helpers";
  import { accounts, links, tags, years, payees } from "./stores";
  import { account_filter, time_filter, fql_filter } from "./stores/filters";
  import AutocompleteInput from "./AutocompleteInput.svelte";

  const filters = [
    {
      name: "time",
      placeholder: _("Time"),
      key: "f t",
      suggestions: $years,
    },
    {
      name: "account",
      placeholder: _("Account"),
      key: "f a",
      suggestions: $accounts,
    },
    {
      name: "filter",
      placeholder: _("Filter by tag, payee, ..."),
      key: "f f",
      suggestions: [
        ...$tags.map((tag) => `#${tag}`),
        ...$links.map((link) => `^${link}`),
        ...$payees.map((payee) => `payee:"${payee}"`),
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

  const values = {};
  account_filter.subscribe((v) => {
    values.account = v;
  });
  fql_filter.subscribe((v) => {
    values.filter = v;
  });
  time_filter.subscribe((v) => {
    values.time = v;
  });

  function submit() {
    account_filter.set(values.account);
    fql_filter.set(values.filter);
    time_filter.set(values.time);
  }

  function clear(name) {
    values[name] = "";
    submit();
  }
</script>

<form id="filter-form" class="filter-form" on:submit|preventDefault={submit}>
  {#each filters as { name, placeholder, key, suggestions, autocompleteOptions }}
    <span class:empty={!values[name]}>
      <AutocompleteInput
        bind:value={values[name]}
        {placeholder}
        {suggestions}
        {key}
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
