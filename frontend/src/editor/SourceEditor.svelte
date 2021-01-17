<script>
  import { onMount } from "svelte";

  import { put, get } from "../api";
  import { bindKey } from "../keyboard-shortcuts";
  import { notify } from "../notifications";
  import router from "../router";
  import { errorCount } from "../stores";

  import {
    initBeancountEditor,
    positionCursorInSourceEditor,
  } from "./init-editor";
  import EditorMenu from "./EditorMenu.svelte";
  import SaveButton from "./SaveButton.svelte";
  import { favaFormat } from "./commands";

  /** @type {{source: string, file_path: string, sha256sum: string, sources: string[]}} */
  export let data;

  /** @type {import('@codemirror/view').EditorView | undefined} */
  let editor;

  let changed = false;

  let file_path = "";
  let sha256sum = "";
  /** @type {string[]} */
  let sources = [];

  let saving = false;

  async function save() {
    if (!editor) {
      return;
    }

    saving = true;
    try {
      sha256sum = await put("source", {
        file_path,
        source: editor.state.doc.toString(),
        sha256sum,
      });
      changed = false;
      editor.focus();
      errorCount.set(await get("errors"));
    } catch (error) {
      notify(error, "error");
    } finally {
      saving = false;
    }
  }

  function checkEditorChanges() {
    if (editor && changed) {
      return "There are unsaved changes. Are you sure you want to leave?";
    }
    return null;
  }

  onMount(() => {
    sha256sum = data.sha256sum;
    file_path = data.file_path;
    sources = data.sources;

    router.interruptHandlers.add(checkEditorChanges);

    // keybindings when the focus is outside the editor
    const unbind = [
      bindKey({ key: "Control+s", mac: "Meta+s" }, (event) => {
        event.preventDefault();
        save();
      }),
      bindKey({ key: "Control+d", mac: "Meta+d" }, (event) => {
        event.preventDefault();
        if (editor) {
          favaFormat(editor);
        }
      }),
    ];

    return () => {
      router.interruptHandlers.delete(checkEditorChanges);
      unbind.forEach((u) => u());
    };
  });

  /**
   * @param {HTMLElement} div
   */
  function sourceEditor(div) {
    editor = initBeancountEditor(
      data.source,
      () => {
        changed = true;
      },
      [
        {
          key: "Control-s",
          mac: "Meta-s",
          run: () => {
            save();
            return true;
          },
        },
      ]
    );
    div.appendChild(editor.dom);
    editor.focus();
    positionCursorInSourceEditor(editor);
    return {
      destroy: () => {
        editor = undefined;
      },
    };
  }

  /**
   * @param {CustomEvent<import("@codemirror/view").Command>} ev
   */
  function command(ev) {
    if (editor) {
      ev.detail(editor);
    }
  }
</script>

<form
  class="fixed-fullsize-container"
  on:submit|preventDefault={save}
  use:sourceEditor
>
  <EditorMenu {file_path} {sources} on:command={command}>
    <SaveButton {changed} {saving} />
  </EditorMenu>
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
    background: var(--color-sidebar-background);
  }
  form :global(.cm-wrap) {
    flex: 1;
    width: 100%;
    height: calc(100% - 44px);
    margin: 0;
  }
  form :global(.cm-lines) {
    border-top: 1px solid var(--color-sidebar-border);
  }
</style>
