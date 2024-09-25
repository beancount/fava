<script lang="ts">
  import type { LanguageSupport } from "@codemirror/language";
  import type { EditorView } from "@codemirror/view";
  import { onMount } from "svelte";

  import { get, put } from "../../api";
  import type { SourceFile } from "../../api/validators";
  import {
    replaceContents,
    scrollToLine,
    setErrors,
  } from "../../codemirror/editor-transactions";
  import { initBeancountEditor } from "../../codemirror/setup";
  import SaveButton from "../../editor/SaveButton.svelte";
  import { log_error } from "../../log";
  import { notify_err } from "../../notifications";
  import router from "../../router";
  import { errors, fava_options } from "../../stores";
  import { searchParams } from "../../stores/url";
  import EditorMenu from "./EditorMenu.svelte";

  export let source: SourceFile;
  export let beancount_language_support: LanguageSupport;

  $: file_path = source.file_path;

  let changed = false;
  const onDocChanges = () => {
    changed = true;
  };

  let sha256sum = "";
  let saving = false;

  /**
   * Save the contents of the editor.
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
      get("errors").then((v) => {
        errors.set(v);
      }, log_error);
    } catch (error) {
      notify_err(error, (e) => e.message);
    } finally {
      saving = false;
    }
  }

  const { editor, renderEditor } = initBeancountEditor(
    "",
    onDocChanges,
    [
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
    ],
    beancount_language_support,
  );

  // update editor contents if source changes
  // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
  $: if (source) {
    editor.dispatch(replaceContents(editor.state, source.source));
    sha256sum = source.sha256sum;
    editor.focus();
    changed = false;
  }

  // wrap this in a function to not trigger the reactive block below
  // on store updates.
  function jumpToInsertOption() {
    const opts = $fava_options.insert_entry.filter(
      (f) => f.filename === file_path,
    );
    const line = parseInt($searchParams.get("line") ?? "0", 10);
    const last_insert_opt = opts[opts.length - 1];
    const lineToScrollTo = (() => {
      if (line > 0) {
        return line;
      }
      if (last_insert_opt) {
        return last_insert_opt.lineno - 1;
      }
      return editor.state.doc.lines;
    })();
    editor.dispatch(scrollToLine(editor.state, lineToScrollTo));
  }

  // Go to line if the edited file changes.
  $: if (file_path) {
    jumpToInsertOption();
  }

  // Update diagnostics, showing errors in the editor
  $: {
    // Only show errors for this file, or general errors (AKA no source)
    const errorsForFile = $errors.filter(
      (err) => err.source === null || err.source.filename === file_path,
    );
    editor.dispatch(setErrors(editor.state, errorsForFile));
  }

  const checkEditorChanges = () =>
    changed
      ? "There are unsaved changes. Are you sure you want to leave?"
      : null;

  onMount(() => router.addInteruptHandler(checkEditorChanges));
</script>

<form
  class="fixed-fullsize-container"
  on:submit|preventDefault={async () => save(editor)}
>
  <EditorMenu {file_path} {editor}>
    <SaveButton {changed} {saving} />
  </EditorMenu>
  <div use:renderEditor />
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
  }

  form div {
    flex: 1;
    width: 100%;
    height: 100px; /* As a flex-base so that it uses exactly the available space. */
  }

  form :global(.cm-editor) {
    width: 100%;
    height: 100%;
    overflow: hidden;
  }
</style>
