<script lang="ts">
  import { urlFor, urlForAccount } from "../helpers";
  import {
    Amount,
    Document,
    EntryMetadata,
    Transaction,
    type Entry,
  } from "../entries";
  import { sort } from "d3-array";
  import { basename } from "../lib/paths";
  import { RawAmount } from "../entries/amount";
  import { currency_name } from "../stores";
  import { ctx } from "../stores/format";

  const shortType: Record<string, string> = {
    Balance: "Bal",
    Close: "Close",
    Document: "Doc",
    Note: "Note",
    Open: "Open",
  };

  interface Props {
    index: number;
    entry: Entry;
    showChangeAndBalance: boolean;
  }

  const { index, entry, showChangeAndBalance }: Props = $props();
  const { t } = entry;

  // svelte-ignore non_reactive_update
  let liClasses = t.toLowerCase();
  if (t === "Custom") liClasses += ` ${entry.type}`;
  if (t === "Transaction") liClasses += ` ${entry.flag}`;

  if (t === "Transaction" || t === "Note" || t == "Document") {
    const { tags } = entry;
    if (tags?.includes("linked")) liClasses += " linked";
    if (tags?.includes("discovered")) liClasses += " discovered";
  }
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
  {#each metadata.entries() as [key, value]}
    <span class="metadata-indicator" title={`${key}: ${value}`}>
      {key.substring(0, 2)}
    </span>
  {/each}
{/snippet}

{#snippet metadata(metadata: EntryMetadata, entryHash: string)}
  {#if !metadata.is_empty()}
    <dl class="metadata">
      {#each metadata.entries() as [key, value]}
        <dt>{key}:</dt>
        <dd>
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
{/snippet}

{#snippet tagsLinks(entry: Document | Transaction)}
  {#each sort(entry.tags ?? []) as tag}
    <span class="tag">{tag}</span>
  {/each}
  {#each sort(entry.links ?? []) as link}
    <span class="link">^{link}</span>
  {/each}
{/snippet}

{#if t !== "Price"}
  <li class={liClasses}>
    <p>
      <span class="datecell" data-sort-value={index}>
        <a href={`#context-${entry.entry_hash}`}>{entry.date}</a>
      </span>
      <span class="flag">
        {#if t === "Transaction"}
          {entry.flag}
        {:else}
          {shortType[t] ?? t.substring(0, 3).toLowerCase()}
        {/if}
      </span>
      {#if t === "Transaction"}
        <span
          class="description droptarget"
          data-entry={entry.entry_hash}
          data-entry-date={entry.date}
          data-account-name={entry.postings[0]?.account}
          >{@render description()}</span
        >
      {:else}
        <span class="description">{@render description()}</span>
      {/if}
      <span class="indicators">
        {@render metadataIndicators(entry.meta)}
        {#if t === "Transaction"}
          {#each entry.postings as posting}
            <!-- TODO: posting flags -->
            <span></span>
            {@render metadataIndicators(posting.meta)}
          {/each}
        {/if}
      </span>
      {#if t === "Balance"}
        <!-- TODO: diff_amount -->
        {@render amount(entry.amount, "num bal")}
        <span class="change num"></span>
        {#if !showChangeAndBalance}
          <span class="change num"></span>
        {/if}
      {/if}
      {#if showChangeAndBalance}
        <!-- TODO -->
      {/if}
    </p>
    {@render metadata(entry.meta, entry.entry_hash)}
    {#if t === "Transaction" && entry.postings.length > 0}
      <ul class="postings">
        {#each entry.postings as posting}
          <!-- TODO: posting flags -->
          <li>
            <p>
              <span class="datecell"></span>
              <span class="flag"></span>
              <!-- TODO: it uses the entry hash, is this correct? -->
              <span
                class="description droptarget"
                data-entry={entry.entry_hash}
                data-account-name={posting.account}
                data-entry-date={entry.date}
              >
                {@render accountLink(posting.account)}
              </span>
              <!-- TODO: cost and price -->
              <span class="num">{posting.amount}</span>
              <span class="num"></span>
              <span class="num"></span>
            </p>
          </li>
        {/each}
      </ul>
    {/if}
  </li>
{/if}

{#snippet description()}
  {#if t === "Open" || t === "Close"}
    {@render accountLink(entry.account)}
  {:else if t === "Note"}
    {entry.comment}
  {:else if t === "Query"}
    <a
      href={$urlFor("report", {
        report_name: "query",
        query_string: `run ${entry.name}`,
      })}
    >
      {entry.name}
    </a>
  {:else if t === "Pad"}
    {@render accountLink(entry.account)}&nbsp;from&nbsp;{@render accountLink(
      entry.source_account,
    )}
  {:else if t === "Custom"}
    <strong>{entry.type}</strong>
    <!-- TODO custom attributes -->
    {#each entry.values as value}
      {value}
    {/each}
  {:else if t === "Document"}
    {@render accountLink(entry.account)}
    <a
      class="filename"
      data-remote
      target="_blank"
      href={$urlFor("document", { filename: entry.filename })}
    >
      {basename(entry.filename)}
    </a>
    {@render tagsLinks(entry)}
  {:else if t === "Balance"}
    {@render accountLink(entry.account)}
    <!-- TODO diff_amount -->
  {:else if t === "Transaction"}
    <strong class="payee">{entry.payee}</strong>
    {#if entry.payee && entry.narration}
      <span class="separator"></span>
    {/if}
    {entry.narration}
    {@render tagsLinks(entry)}
  {/if}
{/snippet}
