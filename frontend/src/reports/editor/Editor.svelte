<script lang="ts">
  import type { EditorView } from "@codemirror/view";
  import { onMount } from "svelte";

  import { get, put } from "../../api";
  import { beancountFormat } from "../../codemirror/beancount-format";
  import { scrollToLine } from "../../codemirror/scroll-to-line";
  import { initBeancountEditor, setErrors } from "../../codemirror/setup";
  import SaveButton from "../../editor/SaveButton.svelte";
  import { bindKey } from "../../keyboard-shortcuts";
  import { log_error } from "../../log";
  import { notify_err } from "../../notifications";
  import router from "../../router";
  import { errors, fava_options } from "../../stores";
  import { searchParams } from "../../stores/url";

  import EditorMenu from "./EditorMenu.svelte";
  import type { PageData } from "./load";

  export let data: PageData;

  $: file_path = data.file_path;

  let changed = false;
  const onDocChanges = () => {
    changed = true;
  };

  let sha256sum = "";
  let saving = false;

  /**
   * Save the contents of the ediftor.
   */
  async function save(cm: EditorView) {
    saving = true;
    try {
      sha256sum = await put("source", {
        file_path,
        source: cm.state.sliceDoc(),
        sha256sum,
      });
      changed = false;
      cm.focus();
      get("errors").then((v) => errors.set(v), log_error);
    } catch (error) {
      notify_err(error, (e) => e.message);
    } finally {
      saving = false;
    }
  }

  const [editor, useEditor] = initBeancountEditor(data.source, onDocChanges, [
    {
      key: "Control-s",
      mac: "Meta-s",
      run: () => {
        save(editor).catch(() => {
          // save should catch all errors itself, see above
        });
        return true;
      },
    },
  ]);

  // update editor contents
  $: if (data) {
    editor.dispatch({
      changes: { from: 0, to: editor.state.doc.length, insert: data.source },
    });
    sha256sum = data.sha256sum;
    editor.focus();
    changed = false;
  }

  // go to line on file changes
  $: if (file_path) {
    const opts = $fava_options.insert_entry.filter(
      (f) => f.filename === file_path
    );
    const line = parseInt($searchParams.get("line") ?? "0", 10);
    if (line > 0) {
      scrollToLine(editor, line);
    } else if (opts.length > 0) {
      const last = opts[opts.length - 1];
      if (last) {
        scrollToLine(editor, last.lineno - 1);
      }
    } else {
      scrollToLine(editor, editor.state.doc.lines);
    }
  }

  // Update diagnostics, showing errors in the editor
  $: {
    const errorsForFile = $errors.filter(
      (error) =>
        // Only show errors for this file, or general errors (AKA no source)
        error.source === null || error.source.filename === file_path
    );
    setErrors(editor, errorsForFile);
  }

  const checkEditorChanges = () =>
    changed
      ? "There are unsaved changes. Are you sure you want to leave?"
      : null;

  onMount(() => router.addInteruptHandler(checkEditorChanges));

  // keybindings when the focus is outside the editor
  onMount(() =>
    bindKey({ key: "Control+s", mac: "Meta+s" }, (event) => {
      event.preventDefault();
      save(editor).catch(() => {
        // save should catch all errors itself, see above
      });
    })
  );
  onMount(() =>
    bindKey({ key: "Control+d", mac: "Meta+d" }, (event) => {
      event.preventDefault();
      beancountFormat(editor);
    })
  );
</script>

<form
  class="fixed-fullsize-container"
  on:submit|preventDefault={() => save(editor)}
>
  <EditorMenu {file_path} {editor}>
    <SaveButton {changed} {saving} />
  </EditorMenu>
  <div use:useEditor />
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
  }

  form div {
    flex: 1;
    width: 100%;
    height: calc(100% - 3rem);
  }

  form :global(.cm-editor) {
    width: 100%;
    height: 100%;
  }
</style>
