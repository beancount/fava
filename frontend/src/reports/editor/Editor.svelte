<script lang="ts">
  import type { EditorView } from "@codemirror/view";
  import { onMount, untrack } from "svelte";

  import { get_errors, put_source } from "../../api/index.ts";
  import {
    replaceContents,
    scrollToLine,
    setErrors,
  } from "../../codemirror/editor-transactions.ts";
  import { initBeancountEditor } from "../../codemirror/setup.ts";
  import SaveButton from "../../editor/SaveButton.svelte";
  import { log_error } from "../../log.ts";
  import { notify_err } from "../../notifications.ts";
  import { router } from "../../router.ts";
  import { insert_entry } from "../../stores/fava_options.ts";
  import { errors } from "../../stores/index.ts";
  import EditorMenu from "./EditorMenu.svelte";
  import type { EditorReportProps } from "./index.ts";

  let {
    source,
    beancount_language_support,
    line_search_param,
  }: EditorReportProps = $props();

  let file_path = $derived(source.file_path);

  let changed = $state(false);
  const onDocChanges = () => {
    changed = true;
  };

  let sha256sum = $state("");
  let saving = $state(false);

  /**
   * Save the contents of the editor.
   */
  async function save(cm: EditorView) {
    saving = true;
    try {
      sha256sum = await put_source({
        file_path,
        source: cm.state.sliceDoc(),
        sha256sum,
      });
      changed = false;
      cm.focus();
      get_errors().then((v) => {
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
    () => beancount_language_support,
  );

  $effect(() => {
    // update editor contents if source changes
    void source;
    untrack(() => {
      editor.dispatch(replaceContents(editor.state, source.source));
      sha256sum = source.sha256sum;
      editor.focus();
      changed = false;
    });
  });

  $effect(() => {
    // Go to line if the edited file changes. The line number is obtained from the
    // URL, last file insert option, or last file line (in that order).
    const last_insert_opt = untrack(() =>
      $insert_entry.filter((f) => f.filename === file_path).at(-1),
    );
    let line = editor.state.doc.lines;
    if (line_search_param != null) {
      line = line_search_param;
    } else if (last_insert_opt) {
      line = last_insert_opt.lineno - 1;
    }
    editor.dispatch(scrollToLine(editor.state, line));
  });

  $effect(() => {
    // Update diagnostics, showing errors in the editor
    // Only show errors for this file, or general errors (AKA no source)
    const errorsForFile = $errors.filter(
      (err) => err.source == null || err.source.filename === file_path,
    );
    editor.dispatch(setErrors(editor.state, errorsForFile));
  });

  const checkEditorChanges = () =>
    changed
      ? "There are unsaved changes. Are you sure you want to leave?"
      : null;

  onMount(() => router.add_interrupt_handler(checkEditorChanges));
</script>

<form
  class="fixed-fullsize-container"
  onsubmit={async (event) => {
    event.preventDefault();
    return save(editor);
  }}
>
  <EditorMenu {file_path} {editor}>
    <SaveButton {changed} {saving} />
  </EditorMenu>
  <div {@attach renderEditor}></div>
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
