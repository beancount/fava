<!--
  @component
  A basic fullsize readonly editor that loads and displays the text document
  at the given URL.
-->
<script lang="ts">
  import { replaceContents } from "../codemirror/editor-transactions";
  import { initDocumentPreviewEditor } from "../codemirror/setup";
  import { fetch, handleText } from "../lib/fetch";

  export let url: string;

  let value = "";

  const { editor, renderEditor } = initDocumentPreviewEditor(value);

  $: fetch(url)
    .then(handleText)
    .then((v) => {
      value = v;
    })
    .catch(() => {
      value = `Loading ${url} failed...`;
    });

  $: if (value !== editor.state.sliceDoc()) {
    editor.dispatch(replaceContents(editor.state, value));
  }
</script>

<div use:renderEditor></div>

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
