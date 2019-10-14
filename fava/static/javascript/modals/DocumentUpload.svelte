<script>
  import router from "../router";
  import { notify } from "../notifications";
  import { _, fetch, handleJSON } from "../helpers";
  import { favaAPI } from "../stores";
  import { account, hash, files } from "../document-upload";

  import ModalBase from "./ModalBase.svelte";
  import AccountInput from "../entry-forms/AccountInput.svelte";

  let form;

  $: shown = $files.length;

  async function submit() {
    await Promise.all(
      $files.map(({ dataTransferFile, name }) => {
        const formData = new FormData(form);
        formData.append("account", $account);
        formData.append("file", dataTransferFile, name);
        return fetch(`${favaAPI.baseURL}api/add-document/`, {
          method: "PUT",
          body: formData,
        })
          .then(handleJSON)
          .then(
            response => {
              notify(response.data);
            },
            error => {
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

<ModalBase {shown} {closeHandler}>
  <form bind:this={form} on:submit|preventDefault={submit}>
    <h3>{_('Upload file(s)')}:</h3>
    {#each $files as file}
      <div class="fieldset">
        <input bind:value={file.name} />
      </div>
    {/each}
    <div class="fieldset">
      <label>
        {_('Documents folder')}:
        <select name="folder">
          {#each favaAPI.options.documents as folder}
            <option>{folder}</option>
          {/each}
        </select>
      </label>
    </div>
    <div class="fieldset">
      <label>
        {_('Account')}:
        <AccountInput bind:value={$account} />
      </label>
      <input type="hidden" name="hash" value={$hash} />
    </div>
    <button type="submit">{_('Upload')}</button>
  </form>
</ModalBase>
