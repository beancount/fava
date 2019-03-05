<script>
  import e from "../events";
  import { _, fetch, handleJSON } from "../helpers";

  import ModalBase from "./ModalBase.svelte";

  let account = "";
  let hash = "";
  let files = [];
  let folders = [];
  let form;

  $: shown = files.length;

  async function submit(event) {
    await Promise.all(
      files.map(({ dataTransferFile, filename }) => {
        const formData = new FormData(form);
        formData.append("file", dataTransferFile, filename);
        console.log(Array.from(formData.entries()));
        return fetch(`${window.favaAPI.baseURL}api/add-document/`, {
          method: "PUT",
          body: formData,
        })
          .then(handleJSON)
          .then(
            data => {
              e.trigger("info", data.message);
            },
            error => {
              e.trigger("error", `Upload error: ${error}`);
            }
          );
      })
    );
    files = [];
    account = "";
    hash = "";
    e.trigger("reload");
  }

  export function handleDrop(event, target) {
    folders = window.favaAPI.options.documents;
    files = [];

    if (!event.dataTransfer.files.length) {
      return;
    }
    if (!folders.length) {
      e.trigger(
        "error",
        _('You need to set the "documents" Beancount option for file uploads.')
      );
      return;
    }

    const dateAttribute = target.getAttribute("data-entry-date");
    const entryDate =
      dateAttribute || new Date().toISOString().substring(0, 10);
    account = target.getAttribute("data-account-name");
    hash = target.getAttribute("data-entry");

    for (const dataTransferFile of event.dataTransfer.files) {
      let name = dataTransferFile.name;

      if (!/^\d{4}-\d{2}-\d{2}/.test(name)) {
        name = `${entryDate} ${name}`;
      }

      files = files.concat({
        dataTransferFile,
        name,
      });
    }

    // TODO: ?? automatic submit if
    // if (form.elements.folder.length > 1 || changedFilename) {
  }
</script>
<ModalBase {shown}>
  <form bind:this="{form}" on:submit|preventDefault="{submit}">
    <h3>{_('Upload file(s)')}:</h3>
    {#each files as file}
    <div class="fieldset">
      <input value="{file.name}" />
    </div>
    {/each}
    <div class="fieldset">
      <label
        >{_('Documents folder')}:
        <select name="folder">
          {#each folders as folder}
          <option>{folder}</option>
          {/each}
        </select>
      </label>
    </div>
    <div class="fieldset">
      <label
        >{_('Account')}:
        <input
          type="text"
          name="account"
          list="accounts"
          bind:value="{account}"
        />
      </label>
      <input type="hidden" name="hash" value="{hash}" />
    </div>
    <button type="submit">{_('Upload')}</button>
  </form>
</ModalBase>
