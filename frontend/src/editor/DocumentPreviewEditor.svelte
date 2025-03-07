<!--
  @component
  A basic fullsize readonly editor that loads and displays the text document
  at the given URL.
-->
<script lang="ts">
  import { replaceContents } from "../codemirror/editor-transactions";
  import { initDocumentPreviewEditor } from "../codemirror/setup";
  import { fetch, handleText } from "../lib/fetch";

  interface Props {
    /** The URL to load the editor contents from. */
    url: string;
  }

  let { url }: Props = $props();

  const { editor, renderEditor } = initDocumentPreviewEditor("");

  const set_editor_content = (value: string) => {
    if (value !== editor.state.sliceDoc()) {
      editor.dispatch(replaceContents(editor.state, value));
    }
  };

  $effect(() => {
    fetch(url)
      .then(handleText)
      .then(set_editor_content, () => {
        set_editor_content(`Loading ${url} failed...`);
      });
  });
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
