<!--
  @component
  A basic fullsize readonly editor that loads and displays the text document
  at the given URL.
-->
<script lang="ts">
  import { initDocumentPreviewEditor } from "../codemirror/setup";
  import { fetch, handleText } from "../lib/fetch";

  export let url: string;

  let value = "";

  const [editor, useEditor] = initDocumentPreviewEditor(value);

  $: fetch(url)
    .then(handleText)
    .then((v) => {
      value = v;
    })
    .catch(() => {
      value = `Loading ${url} failed...`;
    });

  $: if (value !== editor.state.sliceDoc()) {
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

  div :global(.cm-editor) {
    width: 100%;
    height: 100%;
  }
</style>
