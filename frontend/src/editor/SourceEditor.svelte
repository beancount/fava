<script>
  import { onMount } from "svelte";

  import { put, get } from "../api";
  import { bindKey } from "../keyboard-shortcuts";
  import { notify } from "../notifications";
  import router from "../router";
  import { errorCount } from "../stores";
  import { CodeMirror, sourceEditorOptions, initSourceEditor } from "../editor";

  import EditorMenu from "./EditorMenu.svelte";
  import SaveButton from "./SaveButton.svelte";

  /** @type {{source: string, file_path: string, sha256sum: string, sources: string[]}} */
  export let data;

  /** @type {CodeMirror.Editor | undefined} */
  let editor;

  let changed = false;

  let value = "";
  let file_path = "";
  let sha256sum = "";
  /** @type {string[]} */
  let sources = [];

  let saving = false;

  $: if (editor && value !== editor.getValue()) {
    editor.setValue(value);
  }

  async function save() {
    if (!editor) {
      return;
    }

    saving = true;
    try {
      sha256sum = await put("source", {
        file_path,
        source: value,
        sha256sum,
      });
      changed = false;
      editor.focus();
      editor.getDoc().markClean();
      errorCount.set(await get("errors"));
    } catch (error) {
      notify(error, "error");
    } finally {
      saving = false;
    }
  }

  function checkEditorChanges() {
    if (editor && !editor.getDoc().isClean()) {
      return "There are unsaved changes. Are you sure you want to leave?";
    }
    return null;
  }

  onMount(() => {
    sha256sum = data.sha256sum;
    file_path = data.file_path;
    sources = data.sources;

    // keybindings when the focus is outside the editor
    const unbind = [
      ...["Control+s", "Meta+s"].map((key) =>
        bindKey(key, (event) => {
          event.preventDefault();
          save();
        })
      ),
      ...["Control+d", "Meta+d"].map((key) =>
        bindKey(key, (event) => {
          event.preventDefault();
          editor?.execCommand("favaFormat");
        })
      ),
    ];

    router.interruptHandlers.add(checkEditorChanges);

    return () => {
      router.interruptHandlers.delete(checkEditorChanges);
      unbind.forEach((u) => u());
    };
  });

  /**
   * @param {HTMLElement} div
   */
  function sourceEditor(div) {
    value = data.source;
    const options = {
      ...sourceEditorOptions(save),
      autofocus: true,
      value,
    };
    editor = CodeMirror(div, options);
    initSourceEditor(editor);
    editor.on("changes", (cm) => {
      value = cm.getValue();
      changed = !cm.getDoc().isClean();
    });
  }

  /**
   * @param {CustomEvent<string>} ev
   */
  function command(ev) {
    editor?.execCommand(ev.detail);
  }
</script>

<form class="fixed-fullsize-container" on:submit|preventDefault={save}>
  <EditorMenu {file_path} {sources} on:command={command}>
    <SaveButton {changed} {saving} />
  </EditorMenu>
  <div use:sourceEditor />
</form>

<style>
  form {
    background: var(--color-sidebar-background);
  }
  div {
    position: fixed;
    top: calc(var(--header-height) + var(--source-editor-fieldset-height));
    bottom: 0;
    width: 100%;
  }
  div :global(.CodeMirror-lines) {
    border-top: 1px solid var(--color-sidebar-border);
  }
  div :global(.CodeMirror) {
    width: 100%;
    height: 100%;
    margin: 0;
    border: 0;
  }
</style>
