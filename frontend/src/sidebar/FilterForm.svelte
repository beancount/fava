<script lang="ts">
  import AutocompleteInput from "../components/AutocompleteInput.svelte";
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

  function value_extractor(value: string, input: HTMLInputElement) {
    const match = /\S*$/.exec(
      value.slice(0, input.selectionStart ?? undefined),
    );
    return match?.[0] ?? value;
  }
  function value_selector(value: string, input: HTMLInputElement) {
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
    clear_button={true}
    set_size={true}
    onchange={(v: string) => {
      router.set_search_param("time", v);
    }}
  />
  <AutocompleteInput
    value={$account_filter}
    placeholder={_("Account")}
    suggestions={$accounts}
    key="f a"
    clear_button={true}
    set_size={true}
    onchange={(v: string) => {
      router.set_search_param("account", v);
    }}
  />
  <AutocompleteInput
    value={$fql_filter}
    placeholder={_("Filter by tag, payee, …")}
    suggestions={fql_filter_suggestions}
    key="f f"
    clear_button={true}
    set_size={true}
    {value_extractor}
    {value_selector}
    onchange={(v: string) => {
      router.set_search_param("filter", v);
    }}
  />
</div>

<style>
  div {
    --placeholder-color: var(--header-placeholder-color);
    --placeholder-background: var(--header-placeholder-background);
    --input-padding: 8px 25px 8px 10px;

    color: var(--text-color);

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
