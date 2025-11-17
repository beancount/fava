<!--
  @component
  On drag-and-dropping of links (to documents) or files onto an entry or an
  account, this modal overlay allows one to fill in account name and or change
  the file name.

  File uploads via Drag and Drop on elements with class "droptarget"
  and attribute "data-account-name".
-->
<script lang="ts">
  import { SvelteMap } from "svelte/reactivity";

  import { put_add_document, put_attach_document } from "../api/index.ts";
  import AccountInput from "../entry-forms/AccountInput.svelte";
  import { todayAsString } from "../format.ts";
  import { _ } from "../i18n.ts";
  import { get_el } from "../lib/dom.ts";
  import { basename, documentHasAccount } from "../lib/paths.ts";
  import { notify, notify_err } from "../notifications.ts";
  import { router } from "../router.ts";
  import { documents } from "../stores/options.ts";
  import { is_supported_datatransfer } from "./document-upload.ts";
  import ModalBase from "./ModalBase.svelte";

  let account = $state("");
  let files = $state<FileList | null>(null);
  let entry_date = $state<string | null>(null);
  let entry_hash = $state<string | null>(null);
  let documents_folder = $state($documents[0] ?? "");
  const new_file_names = new SvelteMap<File, string>();
  let shown = $derived(files != null);

  /**
   * Handle a dragenter event on '.droptarget'.
   *
   * We want to allow a drop if the dragged thing is either a file that could be
   * dragged from a file manager or a URL (as dragged from a document link in Fava).
   *
   * Setting the .dragover class disables pointer-events on children via CSS, so
   * that the relevant next events are received on this droptarget element.
   *
   * Alternatively, this event can be handled in other components, setting the
   * .dragover class to indicate to the other events handlers below that it is
   * a valid drop zone.
   */
  function ondragenter(event: DragEvent): void {
    if (is_supported_datatransfer(event.dataTransfer)) {
      const droptarget = get_el(event.target)?.closest(".droptarget");
      if (droptarget) {
        droptarget.classList.add("dragover");
        event.preventDefault();
      }
    }
  }

  /**
   * Handle a dragover event
   *
   * If the .dragover class is present, enable it to receive drop events.
   */
  function ondragover(event: DragEvent): void {
    const dragover = get_el(event.target)?.closest(".dragover");
    if (dragover) {
      event.preventDefault();
    }
  }
  /**
   * On dragleave, remove the nearest `.dragover` class.
   */
  function ondragleave(event: DragEvent): void {
    const dragover = get_el(event.target)?.closest(".dragover");
    dragover?.classList.remove("dragover");
  }

  /**
   * On drop, handle both files and links.
   */
  function ondrop(event: DragEvent): void {
    const dragover = get_el(event.target)?.closest(".dragover");
    const { dataTransfer } = event;
    // Account name that the document should be attached to.
    const target_account = dragover?.getAttribute("data-account-name");
    if (dragover == null || target_account == null || dataTransfer == null) {
      return;
    }
    dragover.classList.remove("dragover");
    event.preventDefault();

    if (dataTransfer.types.includes("Files")) {
      // Files are being dropped.
      account = target_account;
      entry_date = dragover.getAttribute("data-entry-date");
      entry_hash = dragover.getAttribute("data-entry-hash");
      files = dataTransfer.files;
    } else if (dataTransfer.types.includes("text/uri-list")) {
      // Links are being dropped
      const url = dataTransfer.getData("URL");
      // Try to extract the filename from the URL.
      let filename = new URL(url).searchParams.get("filename");
      const entry_hash = dragover.getAttribute("data-entry-hash");
      if (filename != null && entry_hash != null) {
        if (documentHasAccount(filename, target_account)) {
          filename = basename(filename);
        }
        put_attach_document({ filename, entry_hash }).then(
          notify,
          (error: unknown) => {
            notify_err(
              error,
              (e) => `Adding document metadata failed: ${e.message}`,
            );
          },
        );
      }
    }
  }

  function closeHandler() {
    account = "";
    entry_date = null;
    entry_hash = null;
    files = null;
    new_file_names.clear();
  }

  function get_name(file: File): string {
    const new_file_name = new_file_names.get(file);
    if (new_file_name != null) {
      return new_file_name;
    }
    return /^\d{4}-\d{2}-\d{2}/.test(file.name)
      ? file.name
      : `${entry_date ?? todayAsString()} ${file.name}`;
  }

  async function onsubmit(event: SubmitEvent) {
    if (files == null) {
      return;
    }
    event.preventDefault();
    await Promise.all(
      Array.from(files).map(async (file) => {
        const formData = new FormData();
        formData.set("account", account);
        if (entry_hash != null) {
          formData.set("hash", entry_hash);
        }
        formData.set("folder", documents_folder);
        const name = get_name(file);
        formData.set("file", file, name);
        return put_add_document(formData).then(notify, (error: unknown) => {
          notify_err(
            error,
            (err) => `Uploading ${name} failed: ${err.message}`,
          );
        });
      }),
    );
    closeHandler();
    router.reload();
  }
</script>

<svelte:document {ondragenter} {ondragover} {ondragleave} {ondrop} />
<ModalBase {shown} {closeHandler}>
  <form {onsubmit}>
    <h3>{_("Upload file(s)")}:</h3>
    <label>
      <span>{_("Files")}:</span>
      <input type="file" multiple bind:files />
    </label>
    {#each files as file (file)}
      <input
        class="file"
        bind:value={
          () => get_name(file),
          (new_file_name: string) => {
            new_file_names.set(file, new_file_name);
          }
        }
      />
    {/each}
    <label>
      <span>{_("Documents folder")}:</span>
      <select bind:value={documents_folder}>
        {#each $documents as folder (folder)}
          <option>{folder}</option>
        {/each}
      </select>
    </label>
    <label>
      <span>{_("Account")}:</span>
      <AccountInput bind:value={account} required />
    </label>
    <button type="submit">{_("Upload")}</button>
  </form>
</ModalBase>

<style>
  input.file {
    width: 100%;
    margin-bottom: 0.5rem;
  }

  label {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;

    > span:first-child {
      flex-basis: 10rem;
    }

    > :global(span):last-child {
      flex: 1;
    }
  }
</style>
