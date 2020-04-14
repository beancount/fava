<script>
  import { onMount } from "svelte";

  import { put } from "../api";
  import { keys } from "../keyboard-shortcuts";
  import { notify } from "../notifications";
  import router from "../router";
  import { fetchErrorCount } from "../stores";
  import { CodeMirror, sourceEditorOptions, initSourceEditor } from "../editor";

  import EditorMenu from "./EditorMenu.svelte";
  import SaveButton from "./SaveButton.svelte";

  export let data;
  let editor;
  let changed = false;

  let value = "";
  let file_path = "";
  let sha256sum = "";
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
      fetchErrorCount();
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

    const unbind = [];
    // keybindings when the focus is outside the editor
    ["Control+s", "Meta+s"].forEach((key) => {
      unbind.push(
        keys.bind(key, (event) => {
          event.preventDefault();
          save();
        })
      );
    });

    ["Control+d", "Meta+d"].forEach((key) => {
      unbind.push(
        keys.bind(key, (event) => {
          event.preventDefault();
          if (editor) {
            editor.execCommand("favaFormat");
          }
        })
      );
    });
    router.interruptHandlers.add(checkEditorChanges);

    return () => {
      router.interruptHandlers.delete(checkEditorChanges);
      unbind.forEach((u) => u());
    };
  });

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

  function command(ev) {
    if (editor) {
      editor.execCommand(ev.detail);
    }
  }
</script>

<style>
  form {
    position: fixed;
    top: var(--header-height);
    right: 0;
    bottom: 0;
    left: var(--aside-width);
    background: var(--color-sidebar-background);
  }
  div {
    position: fixed;
    top: calc(var(--header-height) + var(--source-editor-fieldset-height));
    right: 0;
    bottom: 0;
    left: var(--aside-width);
  }
  @media (max-width: 767px) {
    div,
    form {
      left: 0;
    }
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

<form on:submit|preventDefault={save}>
  <EditorMenu {file_path} {sources} on:command={command}>
    <SaveButton {changed} {saving} />
  </EditorMenu>
  <div use:sourceEditor />
</form>
