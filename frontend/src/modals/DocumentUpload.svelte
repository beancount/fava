<script>
  import router from "../router";
  import { notify } from "../notifications";
  import { put } from "../api";
  import { _ } from "../i18n";
  import { options } from "../stores";
  import { account, hash, files } from "../document-upload";

  import ModalBase from "./ModalBase.svelte";
  import AccountInput from "../entry-forms/AccountInput.svelte";

  /** @type {HTMLFormElement} */
  let form;

  $: shown = !!$files.length;
  $: documents = $options.documents;

  async function submit() {
    await Promise.all(
      $files.map(({ dataTransferFile, name }) => {
        const formData = new FormData(form);
        formData.append("account", $account);
        formData.append("file", dataTransferFile, name);
        return put("add_document", formData).then(
          (response) => {
            notify(response);
          },
          (error) => {
            notify(`Upload error: ${error}`, "error");
          }
        );
      })
    );
    $files = [];
    $account = "";
    $hash = "";
    router.reload();
  }
  function closeHandler() {
    shown = false;
    $files = [];
  }
</script>

<!-- svelte-ignore a11y-label-has-associated-control -->
<ModalBase {shown} {closeHandler}>
  <form bind:this={form} on:submit|preventDefault={submit}>
    <h3>{_("Upload file(s)")}:</h3>
    {#each $files as file}
      <div class="fieldset"><input class="file" bind:value={file.name} /></div>
    {/each}
    <div class="fieldset">
      <label>
        <span>{_("Documents folder")}:</span>
        <select name="folder">
          {#each documents as folder}
            <option>{folder}</option>
          {/each}
        </select>
      </label>
    </div>
    <div class="fieldset account">
      <label>
        <span>{_("Account")}:</span>
        <AccountInput bind:value={$account} />
      </label>
      <input type="hidden" name="hash" value={$hash} />
    </div>
    <button type="submit">{_("Upload")}</button>
  </form>
</ModalBase>

<style>
  input.file {
    width: 100%;
  }

  .fieldset {
    display: "block";
  }

  .fieldset :global(span):first-child {
    margin-right: 8px;
  }

  .fieldset.account :global(span):last-child {
    min-width: 25rem;
  }
</style>
