<script lang="ts">
  import type { EditorView } from "@codemirror/view";
  import { onMount } from "svelte";

  import { get, put } from "../api";
  import { beancountFormat } from "../codemirror/beancount-format";
  import { scrollToLine } from "../codemirror/scroll-to-line";
  import { initBeancountEditor } from "../codemirror/setup";
  import { bindKey } from "../keyboard-shortcuts";
  import { notify } from "../notifications";
  import router from "../router";
  import { errorCount, favaOptions } from "../stores";

  import EditorMenu from "./EditorMenu.svelte";
  import SaveButton from "./SaveButton.svelte";

  export let data: { source: string; file_path: string; sha256sum: string };

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
        file_path: data.file_path,
        source: cm.state.doc.toString(),
        sha256sum,
      });
      changed = false;
      cm.focus();
      get("errors").then((count) => errorCount.set(count));
    } catch (error) {
      if (error instanceof Error) {
        notify(error.message, "error");
      }
    } finally {
      saving = false;
    }
  }

  const [editor, useEditor] = initBeancountEditor(data.source, onDocChanges, [
    {
      key: "Control-s",
      mac: "Meta-s",
      run: () => {
        save(editor);
        return true;
      },
    },
  ]);

  function checkEditorChanges() {
    return changed
      ? "There are unsaved changes. Are you sure you want to leave?"
      : null;
  }

  onMount(() => {
    sha256sum = data.sha256sum;
    router.interruptHandlers.add(checkEditorChanges);

    // keybindings when the focus is outside the editor
    const unbind = [
      bindKey({ key: "Control+s", mac: "Meta+s" }, (event) => {
        event.preventDefault();
        save(editor);
      }),
      bindKey({ key: "Control+d", mac: "Meta+d" }, (event) => {
        event.preventDefault();
        beancountFormat(editor);
      }),
    ];

    editor.focus();
    const opts = $favaOptions.insert_entry.filter(
      (f) => f.filename === data.file_path
    );
    const line = parseInt(
      new URLSearchParams(window.location.search).get("line") ?? "0",
      10
    );
    if (line > 0) {
      scrollToLine(editor, line);
    } else if (opts.length > 0) {
      const last = opts[opts.length - 1];
      scrollToLine(editor, last.lineno - 1);
    } else {
      scrollToLine(editor, editor.state.doc.lines);
    }

    return () => {
      router.interruptHandlers.delete(checkEditorChanges);
      unbind.forEach((u) => u());
    };
  });
</script>

<form
  class="fixed-fullsize-container"
  on:submit|preventDefault={() => save(editor)}
>
  <EditorMenu file_path={data.file_path} {editor}>
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
