<script lang="ts">
  import type { BeancountError } from "../../api/validators";
  import { urlForAccount, urlForSource } from "../../helpers";
  import { _, format } from "../../i18n";
  import { NumberColumn, Sorter, StringColumn } from "../../sort";
  import SortHeader from "../../sort/SortHeader.svelte";
  import { accounts, errors } from "../../stores";

  $: account_re = new RegExp(`(${$accounts.join("|")})`);

  /** Split and extract account names to replace them with links to the account page. */
  function extract_accounts(msg: string): ["text" | "account", string][] {
    return msg
      .split(account_re)
      .map((text, index) =>
        index % 2 === 0 ? ["text", text] : ["account", text],
      );
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
            {@const url = $urlForSource(
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
            <td></td>
            <td class="num"></td>
          {/if}
          <td class="pre">
            {#each extract_accounts(message) as [type, text]}
              {#if type === "text"}
                {text}
              {:else}
                <a href={$urlForAccount(text)}>{text}</a>
              {/if}
            {/each}
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
{:else}
  <p>
    {_("No errors.")}
  </p>
{/if}
