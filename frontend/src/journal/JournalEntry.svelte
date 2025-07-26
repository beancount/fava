<script lang="ts">
  /* eslint-disable @typescript-eslint/no-confusing-void-expression */
  import type { Document, EntryMetadata, Transaction } from "../entries";
  import { type Entry } from "../entries";
  import type { RawAmount } from "../entries/amount";
  import { urlFor, urlForAccount } from "../helpers";
  import { basename } from "../lib/paths";
  import { currency_name } from "../stores";
  import { ctx } from "../stores/format";
  import type { JournalShowEntry } from "../stores/journal";

  interface Props {
    index: number;
    e: Entry;
    showChangeAndBalance: boolean;
    journalShow: Set<JournalShowEntry>;
    li?: HTMLLIElement | undefined;
  }

  let {
    index,
    e,
    showChangeAndBalance,
    journalShow,
    li = $bindable<HTMLLIElement>(),
  }: Props = $props();

  let liClasses = $derived.by(() => {
    const t = e.t;
    let liClasses = t.toLowerCase();
    if (t === "Custom") {
      liClasses += ` ${e.type}`;
    }
    if (t === "Transaction") {
      liClasses += ` ${e.flag}`;
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
</script>

{#snippet amount(amount: RawAmount, cls: string)}
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
  {#if journalShow.has("metadata")}
    {@const entries = metadata.entries()}
    {#if entries.length > 0}
      <dl class="metadata">
        {#each metadata.entries() as [key, value] (key)}
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
  {/if}
{/snippet}

{#snippet tagsLinks(entry: Document | Transaction)}
  {#each entry.tags?.toSorted() ?? [] as tag (tag)}
    <span class="tag">{tag}</span>
  {/each}
  {#each entry.links?.toSorted() ?? [] as link (link)}
    <span class="link">^{link}</span>
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
    <!-- TODO custom attributes -->
    {#each e.values as value (value)}
      {value}
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
    <!-- TODO diff_amount -->
  {:else if e.t === "Transaction"}
    <strong class="payee">{e.payee}</strong>
    {#if e.payee && e.narration}
      <span class="separator"></span>
    {/if}
    {e.narration}
    {@render tagsLinks(e)}
  {/if}
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
    <span class="indicators">
      {@render metadataIndicators(e.meta)}
      {#if e.t === "Transaction"}
        {#each e.postings as posting, index (index)}
          <!-- TODO: posting flags -->
          <span></span>
          {@render metadataIndicators(posting.meta)}
        {/each}
      {/if}
    </span>
    {#if e.t === "Balance"}
      <!-- TODO: diff_amount -->
      {@render amount(e.amount, "num bal")}
      <span class="change num"></span>
      {#if !showChangeAndBalance}
        <span class="change num"></span>
      {/if}
    {/if}
    {#if showChangeAndBalance}
      <!-- TODO -->
    {/if}
  </p>
  {@render metadata(e.meta, e.entry_hash)}
  {#if journalShow.has("postings") && e.t === "Transaction" && e.postings.length > 0}
    <ul class="postings">
      {#each e.postings as posting, index (index)}
        <!-- TODO: posting flags -->
        <li>
          <p>
            <span class="datecell"></span>
            <span class="flag"></span>
            <!-- TODO: it uses the entry hash, is this correct? -->
            <span
              class="description droptarget"
              data-entry={e.entry_hash}
              data-account-name={posting.account}
              data-entry-date={e.date}
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
