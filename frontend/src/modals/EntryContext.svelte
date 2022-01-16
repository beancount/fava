<script lang="ts">
  import type { Entry } from "../entries";
  import { urlForAccount, urlForSource } from "../helpers";
  import { _ } from "../i18n";

  type ContextBalance = Record<string, string[]>;
  export let entry: Entry;
  export let balances_before: ContextBalance | undefined;
  export let balances_after: ContextBalance | undefined;
</script>

<p>
  {_("Location")}:
  <code>
    <a href={urlForSource(entry)}>
      {entry.meta.filename}:{entry.meta.lineno}
    </a>
  </code>
</p>

{#if balances_before && balances_after}
  <details>
    <summary>
      <span>{_("Context")}</span>
    </summary>
    <div>
      <table>
        <thead>
          <tr>
            <th colspan="2">{_("Balances before entry")}</th>
          </tr>
        </thead>
        <tbody>
          {#each Object.entries(balances_before) as [account, inventory]}
            <tr>
              <td><a href={urlForAccount(account)}>{account}</a></td>
              <td>
                {@html inventory.join("<br>")}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      <table>
        <thead>
          <tr>
            <th colspan="2">{_("Balances after entry")}</th>
          </tr>
        </thead>
        <tbody>
          {#each Object.entries(balances_after) as [account, inventory]}
            <tr>
              <td><a href={urlForAccount(account)}>{account}</a></td>
              <td>
                {@html inventory.join("<br>")}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </details>
{/if}
