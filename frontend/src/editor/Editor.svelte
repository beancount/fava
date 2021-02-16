<script lang="ts">
  import { initReadonlyEditor } from "../codemirror/setup";

  export let value: string;

  const [editor, useEditor] = initReadonlyEditor(value);

  $: if (value !== editor.state.doc.toString()) {
    editor.dispatch({
      changes: { from: 0, to: editor.state.doc.length, insert: value },
    });
  }
</script>

<div use:useEditor />

<style>
  div {
    width: 100%;
    height: 100%;
  }
  div :global(.cm-wrap) {
    width: 100%;
    height: 100%;
  }
</style>
