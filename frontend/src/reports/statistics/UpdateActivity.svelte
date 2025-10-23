<script lang="ts">
  import type { AccountDetail } from "../../api/validators.ts";
  import { day } from "../../format.ts";
  import { urlForAccount } from "../../helpers.ts";
  import { _ } from "../../i18n.ts";
  import AccountIndicator from "../../sidebar/AccountIndicator.svelte";
  import {
    NumberColumn,
    Sorter,
    StringColumn,
    UnsortedColumn,
  } from "../../sort/index.ts";
  import SortHeader from "../../sort/SortHeader.svelte";
  import { ctx } from "../../stores/format.ts";
  import { account_details, currency_name } from "../../stores/index.ts";
  import { name_assets, name_liabilities } from "../../stores/options.ts";
  import type { Inventory } from "../query/query_table.ts";

  let { balances }: { balances: Record<string, Inventory> } = $props();

  let accounts = $derived(
    Object.entries($account_details).filter(
      ([account_name]) =>
        account_name.startsWith($name_assets) ||
        account_name.startsWith($name_liabilities),
    ),
  );

  const status_sortorder = { red: 3, yellow: 2, green: 1 };
  type Row = [string, AccountDetail];
  const columns = [
    new StringColumn<Row>(_("Account"), (d) => d[0].valueOf()),
    new NumberColumn<Row>("", ([, d]) =>
      d.uptodate_status == null ? 0 : status_sortorder[d.uptodate_status],
    ),
    new NumberColumn<Row>(_("Last Entry"), ([, d]) =>
      d.last_entry != null ? +d.last_entry.date : 0,
    ),
    new UnsortedColumn(_("Balance")),
  ] as const;
  let sorter = $state(new Sorter(columns[0], "asc"));
  let sorted_accounts = $derived(sorter.sort(accounts));
</script>

<table>
  <thead>
    <tr>
      {#each columns as column (column)}
        <SortHeader bind:sorter {column} />
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each sorted_accounts as [account_name, { last_entry, uptodate_status }] (account_name)}
      {#if last_entry}
        {@const inventory = balances[account_name]}
        <tr>
          <td class="account">
            <a href={$urlForAccount(account_name)}>{account_name}</a>
          </td>
          <td>
            {#if uptodate_status}
              <AccountIndicator account={account_name} small />
            {/if}
          </td>
          <td>
            <a href={`#context-${last_entry.entry_hash}`}>
              {day(last_entry.date)}
            </a>
          </td>
          <td class="num">
            {#if inventory}
              {#each Object.entries(inventory.value) as [currency, number] (currency)}
                <span title={$currency_name(currency)}
                  >{$ctx.amount(number, currency)}</span
                >
                <br />
              {/each}
            {/if}
          </td>
        </tr>
      {/if}
    {/each}
  </tbody>
</table>
