<script lang="ts">
  import type { MouseEventHandler } from "svelte/elements";
  import { addFilter, escape_for_regex } from ".";
  import type { AccountJournalEntry } from "../api/validators";
  import type { Document, EntryMetadata, Transaction } from "../entries";
  import { type Entry } from "../entries";
  import type { Amount, RawAmount } from "../entries/amount";
  import { urlFor, urlForAccount } from "../helpers";
  import { basename } from "../lib/paths";
  import { currency_name } from "../stores";
  import { ctx } from "../stores/format";
  import type { JournalShowEntry } from "../stores/journal";

  interface Props {
    index: number;
    entry: Entry | AccountJournalEntry;
    showChangeAndBalance: boolean;
    journalShow: Set<JournalShowEntry>;
    li?: HTMLLIElement | undefined;
  }

  let {
    index,
    entry,
    showChangeAndBalance,
    journalShow,
    li = $bindable<HTMLLIElement>(),
  }: Props = $props();

  const [e, change, balance] = $derived(
    Array.isArray(entry) ? entry : [entry, null, null],
  );

  const FLAG_TO_TYPES: Record<string, string> = {
    "*": "cleared",
    "!": "pending",
  };

  function flagToTypes(flag: string) {
    return FLAG_TO_TYPES[flag] ?? "other";
  }

  let liClasses = $derived.by(() => {
    const t = e.t;
    let liClasses = t.toLowerCase();
    if (t === "Custom") {
      liClasses += ` ${e.type}`;
    }
    if (t === "Transaction") {
      liClasses += ` ${flagToTypes(e.flag)}`;
    }

    if (t === "Transaction" || t === "Note" || t === "Document") {
      const { tags } = e;
      if (tags?.includes("linked") ?? false) {
        liClasses += " linked";
      }
      if (tags?.includes("discovered") ?? false) {
        liClasses += " discovered";
      }
    }
    return liClasses;
  });

  const unitRegex = /([\d\.\-]+)\s+(\w+)/;
  const costRegex = /\{([\d\.\-]+)\s+(\w+),\s([\w\-]+)\}/;
  const priceRegex = /@\s([\d\.\-]+)\s+(\w+)/;

  type PostingAmounts = [
    [amount: string, currency: string],
    [costAmount: string, costCurrency: string, costDate: string] | null,
    [priceAmount: string, priceCurrency: string] | null,
  ];

  function splitPostingAmount(str: string): PostingAmounts {
    const amount = str.match(unitRegex)!;
    const cost = str.match(costRegex);
    const price = str.match(priceRegex);

    return [
      [amount[1], amount[2]],
      cost ? [cost[1], cost[2], cost[3]] : null,
      price ? [price[1], price[2]] : null,
    ] as PostingAmounts;
  }

  let indicatorToggle = $state(false);
  let showMetadata = $derived(indicatorToggle || journalShow.has("metadata"));
  let showPostings = $derived(indicatorToggle || journalShow.has("postings"));
  function indicatorClick() {
    indicatorToggle = !indicatorToggle;
  }

  type ClickHandler = MouseEventHandler<HTMLElement>;

  const clickTagLink: ClickHandler = ({ currentTarget }) =>
    addFilter(currentTarget.innerText);

  // Note: any special characters in the payee string are escaped so the
  // filter matches against the payee literally.
  const clickPayee: ClickHandler = ({ currentTarget }) =>
    addFilter(`payee:"^${escape_for_regex(currentTarget.innerText)}$"`);

  const clickMetaKey: ClickHandler = ({ currentTarget }) => {
    const expr = `${currentTarget.innerText}""`;
    if (currentTarget.closest(".postings")) {
      // Posting metadata.
      addFilter(`any(${expr})`);
    } else {
      // Entry metadata.
      addFilter(expr);
    }
  };

  const clickMetaVal: ClickHandler = ({ currentTarget }) => {
    const key = (currentTarget.previousElementSibling as HTMLElement).innerText;
    const value = `"^${escape_for_regex(currentTarget.innerText)}$"`;
    const expr = `${key}${value}`;
    if (currentTarget.closest(".postings")) {
      // Posting metadata.
      addFilter(`any(${expr})`);
    } else {
      // Entry metadata.
      addFilter(expr);
    }
  };
</script>

{#snippet amount(amount: Amount | RawAmount, cls: string)}
  {#if !amount.number}
    <span class={cls}></span>
  {:else}
    <span class={cls} title={$currency_name(amount.currency)}>
      {$ctx.amount(+amount.number, amount.currency)}
    </span>
  {/if}
{/snippet}

{#snippet accountLink(name: string)}
  <a href={$urlForAccount(name)}>{name}</a>
{/snippet}

{#snippet metadataIndicators(metadata: EntryMetadata)}
  {#each metadata.entries() as [key, value] (key)}
    <span class="metadata-indicator" title={`${key}: ${value}`}>
      {key.substring(0, 2)}
    </span>
  {/each}
{/snippet}

{#snippet metadata(metadata: EntryMetadata, entryHash: string)}
  {#if showMetadata}
    {@const entries = metadata.entries()}
    {#if entries.length > 0}
      <dl class="metadata">
        {#each entries as [key, value] (key)}
          <dt onclick={clickMetaKey} aria-hidden="true">{key}:</dt>
          <dd onclick={clickMetaVal} aria-hidden="true">
            {#if key.startsWith("document")}
              <a
                class="filename"
                data-remote
                target="_blank"
                href={$urlFor("statement", { entry_hash: entryHash, key: key })}
              >
                {value}
              </a>
            {:else if value.startsWith("http://") || value.startsWith("https://")}
              <a
                class="url"
                data-remote
                target="_blank"
                rel="noopener noreferrer"
                href={value}
              >
                {value}
              </a>
            {:else}
              {value}
            {/if}
          </dd>
        {/each}
      </dl>
    {/if}
  {/if}
{/snippet}

{#snippet tagsLinks(entry: Document | Transaction)}
  {#each entry.tags?.toSorted() ?? [] as tag (tag)}
    <span class="tag" onclick={clickTagLink} aria-hidden="true">#{tag}</span>
  {/each}
  {#each entry.links?.toSorted() ?? [] as link (link)}
    <span class="link" onclick={clickTagLink} aria-hidden="true">^{link}</span>
  {/each}
{/snippet}

{#snippet description()}
  {#if e.t === "Open" || e.t === "Close"}
    {@render accountLink(e.account)}
  {:else if e.t === "Note"}
    {e.comment}
  {:else if e.t === "Query"}
    <a
      href={$urlFor("report", {
        report_name: "query",
        query_string: `run ${e.name}`,
      })}
    >
      {e.name}
    </a>
  {:else if e.t === "Pad"}
    {@render accountLink(e.account)}&nbsp;from&nbsp;{@render accountLink(
      e.source_account,
    )}
  {:else if e.t === "Custom"}
    <strong>{e.type}</strong>
    {#each e.values as { dtype, value }, index (index)}
      {#if index > 0}&nbsp;{/if}{#if dtype === "<AccountDummy>"}
        {@render accountLink(value as string)}
      {:else if dtype === "<class 'beancount.core.amount.Amount'>"}
        {@render amount(value as Amount, "num")}
      {:else if dtype === "<class 'str'>"}"{value}"
      {:else if dtype === "<class 'bool'>"}{value}
      {:else if dtype === "<class 'datetime.date'>"}{value}{/if}
    {/each}
  {:else if e.t === "Document"}
    {@render accountLink(e.account)}
    <a
      class="filename"
      data-remote
      target="_blank"
      href={$urlFor("document", { filename: e.filename })}
    >
      {basename(e.filename)}
    </a>
    {@render tagsLinks(e)}
  {:else if e.t === "Balance"}
    {@render accountLink(e.account)}
    {#if e.diff_amount}
      <span class="spacer"></span>
      accumulated
      <span class="num">
        {$ctx.amount(
          +e.amount.number + e.diff_amount.number,
          e.amount.currency,
        )}
      </span>
    {/if}
  {:else if e.t === "Transaction"}
    <strong class="payee" onclick={clickPayee} aria-hidden="true"
      >{e.payee}</strong
    >{#if e.payee && e.narration}<span class="separator"
      ></span>{/if}{e.narration}
    {@render tagsLinks(e)}
  {/if}
{/snippet}

{#snippet postingAmount([unit, cost, price]: PostingAmounts)}
  <span class="num">{$ctx.amount(+unit[0], unit[1])}</span>
  <span class="num"
    >{#if cost}{$ctx.amount(+cost[0], cost[1])}, {cost[2]}{/if}</span
  >
  <span class="num">{price ? $ctx.amount(+price[0], price[1]) : ""}</span>
{/snippet}

<li class={liClasses} bind:this={li} data-index={index}>
  <p>
    <span class="datecell" data-sort-value={index}>
      <a href={`#context-${e.entry_hash}`}>{e.date}</a>
    </span>
    <span class="flag">{e.sortFlag}</span>
    {#if e.t === "Transaction"}
      <span
        class="description droptarget"
        data-entry={e.entry_hash}
        data-entry-date={e.date}
        data-account-name={e.postings[0]?.account}>{@render description()}</span
      >
    {:else}
      <span class="description">{@render description()}</span>
    {/if}
    <span class="indicators" onclick={indicatorClick} aria-hidden="true">
      {@render metadataIndicators(e.meta)}
      {#if e.t === "Transaction"}
        {#each e.postings as posting, index (index)}
          <span class={posting.flag ? flagToTypes(posting.flag) : null}></span>
          {@render metadataIndicators(posting.meta)}
        {/each}
      {/if}
    </span>
    {#if e.t === "Balance"}
      {@render amount(e.amount, "num bal" + (e.diff_amount ? " pending" : ""))}
      {#if e.diff_amount}
        {@render amount(e.diff_amount, "change num bal pending")}
      {:else}
        <span class="change num"></span>
      {/if}
      {#if !showChangeAndBalance}
        <span class="change num"></span>
      {/if}
    {/if}
    {#if showChangeAndBalance}
      {#if e.t === "Transaction"}
        <span class="change num">
          {#each Object.entries(change ?? {}) as [currency, number]}
            {$ctx.amount(number, currency)}<br />
          {/each}
        </span>
      {/if}
      <span class="num">
        {#each Object.entries(balance ?? {}) as [currency, number]}
          {$ctx.amount(number, currency)}<br />
        {/each}
      </span>
    {/if}
  </p>
  {@render metadata(e.meta, e.entry_hash)}
  {#if showPostings && e.t === "Transaction" && e.postings.length > 0}
    <ul class="postings">
      {#each e.postings as posting, index (index)}
        <li class={posting.flag ? flagToTypes(posting.flag) : null}>
          <p>
            <span class="datecell"></span>
            <span class="flag">{posting.flag ?? ""}</span>
            <!-- TODO: it uses the entry hash, is this correct? -->
            <span
              class="description droptarget"
              data-entry={e.entry_hash}
              data-account-name={posting.account}
              data-entry-date={e.date}
            >
              {@render accountLink(posting.account)}
            </span>
            {@render postingAmount(splitPostingAmount(posting.amount))}
          </p>
          {@render metadata(posting.meta, e.entry_hash)}
        </li>
      {/each}
    </ul>
  {/if}
</li>
