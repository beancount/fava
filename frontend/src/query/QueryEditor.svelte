<script>
  import CodeMirror from "codemirror";
  import { createEventDispatcher } from "svelte";

  import { enableAutomaticCompletions } from "../editor";
  import { _ } from "../i18n";
  import { keyboardShortcut } from "../keyboard-shortcuts";

  /** @type {string} */
  export let value;
  /** @type {CodeMirror.Editor} */
  let editor;
  const dispatch = createEventDispatcher();

  $: if (editor && value !== editor.getValue()) {
    editor.setValue(value);
  }

  /**
   * @param {HTMLElement} form
   */
  function queryEditor(form) {
    const queryOptions = {
      value,
      mode: "beancount-query",
      extraKeys: {
        "Ctrl-Enter": () => dispatch("submit"),
        "Cmd-Enter": () => dispatch("submit"),
      },
      placeholder: _(
        "...enter a BQL query. 'help' to list available commands."
      ),
    };
    editor = CodeMirror((cm) => {
      form.insertBefore(cm, form.firstChild);
    }, queryOptions);

    editor.on("change", (cm) => {
      value = cm.getValue();
    });

    enableAutomaticCompletions(editor);
  }
</script>

<form use:queryEditor on:submit|preventDefault={() => dispatch("submit")}>
  <button type="submit" use:keyboardShortcut={"Control+Enter"}
    >{_("Submit")}</button
  >
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

  form :global(.CodeMirror) {
    flex-grow: 1;
    width: 100%;
    height: auto;
    margin: 0;
    margin-right: 0.5em;
    font-family: var(--font-family-editor);
    font-size: 16px;
    border: 1px solid var(--color-background-darker);
  }
</style>
