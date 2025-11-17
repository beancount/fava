<script lang="ts">
  import { urlForAccount } from "../helpers.ts";
  import { _ } from "../i18n.ts";

  type ContextBalance = Record<string, string[]>;
  interface Props {
    balances_before: ContextBalance;
    balances_after: ContextBalance | null;
  }

  let { balances_before, balances_after }: Props = $props();

  let accounts = $derived(
    [
      ...new Set([
        ...Object.keys(balances_before),
        ...Object.keys(balances_after ?? {}),
      ]),
    ].sort(),
  );
</script>

<details>
  <summary>
    <span>{_("Context")}</span>
  </summary>
  <div>
    <table>
      <thead>
        <tr>
          <th>{_("Account")}</th>
          <th>{_("Balances before entry")}</th>
          {#if balances_after}
            <th>{_("Balances after entry")}</th>
          {/if}
        </tr>
      </thead>
      <tbody>
        {#each accounts as account (account)}
          <tr>
            <td><a href={$urlForAccount(account)}>{account}</a></td>
            <td class="num">
              {#each balances_before[account] as amount (amount)}
                {amount}
                <br />
              {/each}
            </td>
            {#if balances_after}
              <td class="num">
                {#each balances_after[account] as amount (amount)}
                  {amount}
                  <br />
                {/each}
              </td>
            {/if}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</details>
