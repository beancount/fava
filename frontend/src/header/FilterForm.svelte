<script>
  import { _ } from "../i18n";
  import { accounts, links, tags, years, payees } from "../stores";
  import { account_filter, time_filter, fql_filter } from "../stores/filters";
  import AutocompleteInput from "../AutocompleteInput.svelte";

  $: fql_filter_suggestions = [
    ...$tags.map((tag) => `#${tag}`),
    ...$links.map((link) => `^${link}`),
    ...$payees.map((payee) => `payee:"${payee}"`),
  ];

  /**
   * @param {string} value
   * @param {HTMLInputElement} input
   */
  function valueExtractor(value, input) {
    const match = value
      .slice(0, input.selectionStart || undefined)
      .match(/\S*$/);
    return match ? match[0] : value;
  }
  /**
   * @param {string} value
   * @param {HTMLInputElement} input
   */
  function valueSelector(value, input) {
    const selectionStart = input.selectionStart || 0;
    const match = input.value.slice(0, selectionStart).match(/\S*$/);
    return match
      ? `${input.value.slice(
          0,
          selectionStart - match[0].length
        )}${value}${input.value.slice(selectionStart)}`
      : value;
  }

  let account_filter_value = "";
  let fql_filter_value = "";
  let time_filter_value = "";
  account_filter.subscribe((v) => {
    account_filter_value = v;
  });
  fql_filter.subscribe((v) => {
    fql_filter_value = v;
  });
  time_filter.subscribe((v) => {
    time_filter_value = v;
  });

  function submit() {
    account_filter.set(account_filter_value);
    fql_filter.set(fql_filter_value);
    time_filter.set(time_filter_value);
  }
</script>

<form on:submit|preventDefault={submit}>
  <AutocompleteInput
    bind:value={time_filter_value}
    placeholder={_("Time")}
    suggestions={$years}
    key="f t"
    clearButton={true}
    setSize={true}
    on:blur={submit}
    on:select={submit}
  />
  <AutocompleteInput
    bind:value={account_filter_value}
    placeholder={_("Account")}
    suggestions={$accounts}
    key="f a"
    clearButton={true}
    setSize={true}
    on:blur={submit}
    on:select={submit}
  />
  <AutocompleteInput
    bind:value={fql_filter_value}
    placeholder={_("Filter by tag, payee, ...")}
    suggestions={fql_filter_suggestions}
    key="f f"
    clearButton={true}
    setSize={true}
    {valueExtractor}
    {valueSelector}
    on:blur={submit}
    on:select={submit}
  />
  <button type="submit" />
</form>

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
