<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { _ } from "../i18n.ts";
  import { escape_for_regex } from "../lib/regex.ts";
  import { router } from "../router.ts";
  import {
    account_filter,
    fql_filter,
    time_filter,
  } from "../stores/filters.ts";
  import { accounts, links, payees, tags, years } from "../stores/index.ts";

  let fql_filter_suggestions = $derived([
    ...$tags.map((tag) => `#${tag}`),
    ...$links.map((link) => `^${link}`),
    ...$payees.map((payee) => `payee:"${escape_for_regex(payee)}"`),
  ]);

  function valueExtractor(value: string, input: HTMLInputElement) {
    const match = /\S*$/.exec(
      value.slice(0, input.selectionStart ?? undefined),
    );
    return match?.[0] ?? value;
  }
  function valueSelector(value: string, input: HTMLInputElement) {
    const selectionStart = input.selectionStart ?? 0;
    const match = /\S*$/.exec(input.value.slice(0, selectionStart));
    const matchLength = match?.[0]?.length;
    return matchLength !== undefined
      ? `${input.value.slice(
          0,
          selectionStart - matchLength,
        )}${value}${input.value.slice(selectionStart)}`
      : value;
  }
</script>

<div class="flex-row">
  <AutocompleteInput
    value={$time_filter}
    placeholder={_("Time")}
    suggestions={$years}
    key="f t"
    clearButton={true}
    setSize={true}
    onchange={(v: string) => {
      router.set_search_param("time", v);
    }}
  />
  <AutocompleteInput
    value={$account_filter}
    placeholder={_("Account")}
    suggestions={$accounts}
    key="f a"
    clearButton={true}
    setSize={true}
    onchange={(v: string) => {
      router.set_search_param("account", v);
    }}
  />
  <AutocompleteInput
    value={$fql_filter}
    placeholder={_("Filter by tag, payee, …")}
    suggestions={fql_filter_suggestions}
    key="f f"
    clearButton={true}
    setSize={true}
    {valueExtractor}
    {valueSelector}
    onchange={(v: string) => {
      router.set_search_param("filter", v);
    }}
  />
</div>

<style>
  div {
    color: var(--text-color);

    --placeholder-color: var(--header-placeholder-color);
    --placeholder-background: var(--header-placeholder-background);
    --input-padding: 8px 25px 8px 10px;

    & > :global(span) {
      max-width: 18rem;
    }

    & :global(input) {
      outline: none;
      background-color: var(--background);
      border: 0;
    }

    & :global([type="text"]:focus) {
      background-color: var(--background);
    }
  }

  @media print {
    div {
      --input-padding: 8px 10px;

      & :global(input):placeholder-shown {
        display: none;
      }
    }
  }
</style>
