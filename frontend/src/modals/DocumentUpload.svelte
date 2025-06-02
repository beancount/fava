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
  import { documents } from "../stores/options";
  import ModalBase from "./ModalBase.svelte";

  let shown = $derived(!!$files.length);

  let documents_folder = $state("");

  function closeHandler() {
    $files = [];
    $account = "";
    $hash = "";
  }

  async function submit(event: SubmitEvent) {
    event.preventDefault();
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
  <form onsubmit={submit}>
    <h3>{_("Upload file(s)")}:</h3>
    {#each $files as file (file.dataTransferFile)}
      <div class="fieldset">
        <input class="file" bind:value={file.name} />
      </div>
    {/each}
    <div class="fieldset">
      <label>
        <span>{_("Documents folder")}:</span>
        <select bind:value={documents_folder}>
          {#each $documents as folder (folder)}
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

  .fieldset > label > :global(span):first-child {
    margin-right: 8px;
  }

  .fieldset.account > label > :global(span):last-child {
    min-width: 25rem;
  }
</style>
