<script>
  import { _ } from "./helpers";
  import { accounts, links, tags, years, payees } from "./stores";
  import { account_filter, time_filter, fql_filter } from "./stores/filters";
  import AutocompleteInput from "./AutocompleteInput.svelte";

  $: fql_filter_suggestions = [
    ...$tags.map((tag) => `#${tag}`),
    ...$links.map((link) => `^${link}`),
    ...$payees.map((payee) => `payee:"${payee}"`),
  ];

  function valueExtractor(value, input) {
    const [ret] = value.slice(0, input.selectionStart).match(/\S*$/);
    return ret;
  }
  function valueSelector(value, input) {
    const [search] = input.value.slice(0, input.selectionStart).match(/\S*$/);
    return `${input.value.slice(
      0,
      input.selectionStart - search.length
    )}${value}${input.value.slice(input.selectionStart)}`;
  }

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
</script>

<style>
  form {
    display: flex;
    flex-wrap: wrap;
    padding-top: 7px;
    margin: 0;
    color: var(--color-text);

    --color-placeholder: var(--color-header-tinted);
    --background-placeholder: var(--color-header-light);
  }

  form > :global(span) {
    max-width: 18rem;
    margin: 0 4px 6px 0;
  }

  form :global(input) {
    padding: 8px 25px 8px 10px;
    background-color: var(--color-background);
    border: 0;
    outline: none;
  }

  form :global([type="text"]:focus) {
    background-color: var(--color-background);
  }

  [type="submit"] {
    display: none;
  }

  @media print {
    form {
      display: none;
    }
  }
</style>

<form on:submit|preventDefault={submit}>
  <AutocompleteInput
    bind:value={values.time}
    placeholder={_('Time')}
    suggestions={$years}
    key="f t"
    clearButton={true}
    setSize={true}
    on:blur={submit}
    on:select={submit} />
  <AutocompleteInput
    bind:value={values.account}
    placeholder={_('Account')}
    suggestions={$accounts}
    key="f a"
    clearButton={true}
    setSize={true}
    on:blur={submit}
    on:select={submit} />
  <AutocompleteInput
    bind:value={values.filter}
    placeholder={_('Filter by tag, payee, ...')}
    suggestions={fql_filter_suggestions}
    key="f f"
    clearButton={true}
    setSize={true}
    {valueExtractor}
    {valueSelector}
    on:blur={submit}
    on:select={submit} />
  <button type="submit" />
</form>
