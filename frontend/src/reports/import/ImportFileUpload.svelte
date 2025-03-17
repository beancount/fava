<script lang="ts">
  import { put } from "../../api";
  import { _ } from "../../i18n";
  import { notify, notify_err } from "../../notifications";
  import router from "../../router";

  let input: HTMLInputElement | undefined = $state.raw();

  /** Upload the selected files and reload. */
  async function uploadImports(event: SubmitEvent) {
    event.preventDefault();
    if (input?.files == null) {
      return;
    }
    await Promise.all(
      Array.from(input.files).map(async (file) => {
        const formData = new FormData();
        formData.append("file", file, file.name);
        return put("upload_import_file", formData).then(
          notify,
          (error: unknown) => {
            notify_err(error, (err) => `Upload error: ${err.message}`);
          },
        );
      }),
    );
    input.value = "";
    router.reload();
  }
</script>

<form onsubmit={uploadImports}>
  <h2>{_("Upload files for import")}</h2>
  <input bind:this={input} multiple type="file" />
  <button type="submit">{_("Upload")}</button>
</form>
