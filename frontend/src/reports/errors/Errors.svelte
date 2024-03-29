<script lang="ts">
  import type { BeancountError } from "../../api/validators";
  import { urlForAccount, urlForSource } from "../../helpers";
  import { _, format } from "../../i18n";
  import { NumberColumn, Sorter, StringColumn } from "../../sort";
  import SortHeader from "../../sort/SortHeader.svelte";
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
        el.href = $urlForAccount(s);
        el.textContent = s;
        return el;
      })
      .map((el) => el.outerHTML)
      .join("");
  }

  type T = BeancountError;
  const columns = [
    new StringColumn<T>(_("File"), (d) => d.source?.filename ?? ""),
    new NumberColumn<T>(_("Line"), (d) => d.source?.lineno ?? 0),
    new StringColumn<T>(_("Error"), (d) => d.message),
  ] as const;
  let sorter = new Sorter(columns[0], "desc");

  $: sorted_errors = sorter.sort($errors);
</script>

{#if $errors.length}
  <table class="errors">
    <thead>
      <tr>
        {#each columns as column}
          <SortHeader bind:sorter {column} />
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each sorted_errors as { message, source }}
        <tr>
          {#if source}
            {@const url = urlForSource(
              source.filename,
              source.lineno.toString(),
            )}
            {@const title = format(_("Show source %(file)s:%(lineno)s"), {
              file: source.filename,
              lineno: source.lineno.toString(),
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
