<script>
  import { onMount } from "svelte";

  import { put, get } from "../api";
  import { bindKey } from "../keyboard-shortcuts";
  import { notify } from "../notifications";
  import router from "../router";
  import { errorCount } from "../stores";

  import { initBeancountEditor } from "../codemirror/setup";
  import { positionCursorInSourceEditor } from "../codemirror/position-cursor";
  import EditorMenu from "./EditorMenu.svelte";
  import SaveButton from "./SaveButton.svelte";
  import { beancountFormat } from "../codemirror/beancount-format";

  /** @type {{source: string, file_path: string, sha256sum: string}} */
  export let data;

  let changed = false;
  const onDocChanges = () => {
    changed = true;
  };

  let sha256sum = "";
  let saving = false;

  /**
   * Save the contents of the editor.
   * @param {import("@codemirror/view").EditorView} cm
   */
  async function save(cm) {
    saving = true;
    try {
      sha256sum = await put("source", {
        file_path: data.file_path,
        source: cm.state.doc.toString(),
        sha256sum,
      });
      changed = false;
      cm.focus();
      errorCount.set(await get("errors"));
    } catch (error) {
      notify(error, "error");
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
    const line = parseInt(
      new URLSearchParams(window.location.search).get("line") ?? "0",
      10
    );
    positionCursorInSourceEditor(editor, line);

    return () => {
      router.interruptHandlers.delete(checkEditorChanges);
      unbind.forEach((u) => u());
    };
  });

  /**
   * @param {CustomEvent<import("@codemirror/view").Command>} ev
   */
  function command(ev) {
    ev.detail(editor);
  }
</script>

<form
  class="fixed-fullsize-container"
  on:submit|preventDefault={() => save(editor)}
  use:useEditor
>
  <EditorMenu file_path={data.file_path} on:command={command}>
    <SaveButton {changed} {saving} />
  </EditorMenu>
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
  }
  form :global(.cm-wrap) {
    flex: 1;
    width: 100%;
    height: calc(100% - 3rem);
  }
</style>
