<script lang="ts">
  import { replaceContents } from "../../codemirror/editor-transactions";
  import { initQueryEditor } from "../../codemirror/setup";
  import { _ } from "../../i18n";
  import { keyboardShortcut } from "../../keyboard-shortcuts";

  interface Props {
    value: string;
    submit: () => void;
  }

  let { value = $bindable(), submit }: Props = $props();

  const { editor, renderEditor } = initQueryEditor(
    value,
    (state) => {
      value = state.sliceDoc();
    },
    _("...enter a BQL query. 'help' to list available commands."),
    submit,
  );

  $effect(() => {
    if (value !== editor.state.sliceDoc()) {
      editor.dispatch(replaceContents(editor.state, value));
    }
  });
</script>

<form
  onsubmit={(event) => {
    event.preventDefault();
    submit();
  }}
>
  <div use:renderEditor></div>
  <button type="submit" use:keyboardShortcut={"Control+Enter"}>
    {_("Submit")}
  </button>
</form>

<style>
  form {
    display: flex;
    align-items: center;
    padding-bottom: 1em;
  }

  button {
    margin: 0;
  }

  div {
    flex-grow: 1;
    width: 100%;
    height: auto;
    margin-right: 0.5em;
    font-size: 16px;
    border: 1px solid var(--border);
  }

  form :global(.cm-editor) {
    width: 100%;
  }
</style>
