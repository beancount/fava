<script lang="ts">
  import { attach_editor } from "../../codemirror/dom.ts";
  import type { CodemirrorBql } from "../../codemirror/types.ts";
  import { _ } from "../../i18n.ts";
  import { keyboardShortcut } from "../../keyboard-shortcuts.ts";

  interface Props {
    value: string;
    submit: () => void;
    codemirror_bql: CodemirrorBql;
  }

  let { value = $bindable(), submit, codemirror_bql }: Props = $props();

  // svelte-ignore state_referenced_locally
  const editor = codemirror_bql.init_query_editor(
    value,
    (state) => {
      value = state.sliceDoc();
    },
    _("...enter a BQL query. 'help' to list available commands."),
    () => submit,
  );

  $effect(() => {
    if (value !== editor.state.sliceDoc()) {
      editor.dispatch(codemirror_bql.replace_contents(editor.state, value));
    }
  });
</script>

<form
  onsubmit={(event) => {
    event.preventDefault();
    submit();
  }}
>
  <div {@attach attach_editor(editor)}></div>
  <button type="submit" {@attach keyboardShortcut("Control+Enter")}>
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
