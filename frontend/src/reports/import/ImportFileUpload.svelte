<script lang="ts">
  import { put_upload_import_file } from "../../api/index.ts";
  import { _ } from "../../i18n.ts";
  import { notify, notify_err } from "../../notifications.ts";
  import { router } from "../../router.ts";

  let input: HTMLInputElement | undefined = $state.raw();

  /** Upload the selected files and reload. */
  async function upload_imports(event: SubmitEvent) {
    event.preventDefault();
    if (input?.files == null) {
      return;
    }
    const files = Array.from(input.files);
    await Promise.all(
      files.map(async (file) => {
        const form_data = new FormData();
        form_data.append("file", file, file.name);
        return put_upload_import_file(form_data).then(
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

<form onsubmit={upload_imports}>
  <h2>{_("Upload files for import")}</h2>
  <input bind:this={input} multiple type="file" />
  <button type="submit">{_("Upload")}</button>
</form>
