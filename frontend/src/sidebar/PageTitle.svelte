<script lang="ts">
  import { urlForAccount } from "../helpers";

  import { page_title } from "./page-title";

  $: ({ title, type } = $page_title);

  $: is_account = type === "account";
</script>

<strong>
  {#if !is_account}
    {title}
  {:else}
    {@const parts = title.split(":")}
    <span class="droptarget" data-account-name={title}>
      {#each parts as part, index}
        {@const name = parts.slice(0, index + 1).join(":")}<a
          href={urlForAccount(name)}
          title={name}>{part}</a
        >{#if index < parts.length - 1}:{/if}{/each}
    </span>
  {/if}
</strong>

<!-- 
  TODO
  {%- if account_name and ledger.accounts[account_name].meta.get('fava-uptodate-indication') -%}
  {{ indicator(ledger, account_name) }}
  {{ last_account_activity(ledger, account_name) }}
  {%- endif -%}

  {%- set last_entry = ledger.last_entry(account_name) -%}
  {%- if last_entry -%}
  <span class="last-activity">
    (Last entry: <a href="#context-{{ last_entry|hash_entry }}">{{ last_entry.date }}</a>)
  </span>
  {%- endif -%}
 -->
<style>
  a {
    color: unset;
  }

  strong::before {
    margin: 0 10px;
    font-weight: normal;
    content: "›";
    opacity: 0.5;
  }

  .droptarget {
    padding: 0.6em;
    margin-left: -0.6em;
  }

  /* .last-activity {
    display: inline-block;
    margin-left: 10px;
    font-size: 12px;
    font-weight: normal;
    opacity: 80%;
  }

  .status-indicator {
    width: 10px;
    height: 10px;
    margin: 0 0 0 10px;
    border-radius: 10px;
  }

  .status-indicator.status-gray {
    margin-left: 0;
  } */
</style>
