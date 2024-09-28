<!--
  @component
  On drag-and-dropping of links (to documents) or files onto an entry or an
  account, this modal overlay allows one to fill in account name and or change
  the file name.
-->
<script lang="ts">
  import { put } from "../api";
  import { account, files, hash } from "../document-upload";
  import AccountInput from "../entry-forms/AccountInput.svelte";
  import { _ } from "../i18n";
  import { notify, notify_err } from "../notifications";
  import router from "../router";
  import { options } from "../stores";
  import ModalBase from "./ModalBase.svelte";

  $: shown = !!$files.length;
  $: documents = $options.documents;

  let documents_folder = "";

  function closeHandler() {
    $files = [];
    $account = "";
    $hash = "";
  }

  async function submit() {
    await Promise.all(
      $files.map(async ({ dataTransferFile, name }) => {
        const formData = new FormData();
        formData.append("account", $account);
        formData.append("hash", $hash);
        formData.append("folder", documents_folder);
        formData.append("file", dataTransferFile, name);
        return put("add_document", formData).then(notify, (error: unknown) => {
          notify_err(error, (err) => `Upload error: ${err.message}`);
        });
      }),
    );
    closeHandler();
    router.reload();
  }
</script>

<ModalBase {shown} {closeHandler}>
  <form on:submit|preventDefault={submit}>
    <h3>{_("Upload file(s)")}:</h3>
    {#each $files as file}
      <div class="fieldset">
        <input class="file" bind:value={file.name} />
      </div>
    {/each}
    <div class="fieldset">
      <label>
        <span>{_("Documents folder")}:</span>
        <select bind:value={documents_folder}>
          {#each documents as folder}
            <option>{folder}</option>
          {/each}
        </select>
      </label>
    </div>
    <div class="fieldset account">
      <!-- svelte-ignore a11y-label-has-associated-control -->
      <label>
        <span>{_("Account")}:</span>
        <AccountInput bind:value={$account} />
      </label>
    </div>
    <button type="submit">{_("Upload")}</button>
  </form>
</ModalBase>

<style>
  input.file {
    width: 100%;
  }

  .fieldset {
    margin-bottom: 6px;
  }

  .fieldset :global(span):first-child {
    margin-right: 8px;
  }

  .fieldset.account :global(span):last-child {
    min-width: 25rem;
  }
</style>
