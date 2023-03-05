<script lang="ts">
  import { urlForAccount, urlForSource } from "../../helpers";
  import { _, format } from "../../i18n";
  import { sortableTable } from "../../sort";
  import { accounts, errors } from "../../stores";

  $: account_re = new RegExp(`(${$accounts.join("|")})`);

  /** Replace all account names with links to the corresponding account page. */
  function addAccountLinks(msg: string): string {
    return msg
      .split(account_re)
      .map((s, idx) => {
        if (idx % 2 === 0) {
          const el = document.createElement("span");
          el.textContent = s;
          return el;
        }
        const el = document.createElement("a");
        el.href = urlForAccount(s);
        el.textContent = s;
        return el;
      })
      .map((el) => el.outerHTML)
      .join("");
  }
</script>

{#if $errors.length}
  <table use:sortableTable class="errors">
    <thead>
      <tr>
        <th data-sort="string">{_("File")}</th>
        <th data-sort="num">{_("Line")}</th>
        <th data-sort="string">{_("Error")}</th>
      </tr>
    </thead>
    <tbody>
      {#each $errors as { message, source }}
        <tr>
          {#if source}
            {@const url = urlForSource(source.filename, `${source.lineno}`)}
            {@const title = format(_("Show source %(file)s:%(lineno)s"), {
              file: source.filename,
              lineno: `${source.lineno}`,
            })}
            <td>{source.filename}</td>
            <td class="num">
              <a class="source" href={url} {title}>{source.lineno}</a>
            </td>
          {:else}
            <td />
            <td class="num" />
          {/if}
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          <td class="pre">{@html addAccountLinks(message)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{:else}
  <p>
    {_("No errors.")}
  </p>
{/if}
