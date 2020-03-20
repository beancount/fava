<script>
  import CodeMirror from "codemirror";
  import { createEventDispatcher } from "svelte";

  import { ignoreKey } from "../editor";
  import { _ } from "../helpers";

  export let value;
  let editor;
  const dispatch = createEventDispatcher();

  $: if (editor && value !== editor.getValue()) {
    editor.setValue(value);
  }

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
    editor = CodeMirror(cm => {
      form.insertBefore(cm, form.firstChild);
    }, queryOptions);

    editor.on("change", cm => {
      value = cm.getValue();
    });

    editor.on("keyup", (cm, event) => {
      if (!cm.state.completionActive && !ignoreKey(event.key)) {
        CodeMirror.commands.autocomplete(cm, undefined, {
          completeSingle: false,
        });
      }
    });
  }
</script>

<form
  on:submit|preventDefault={() => dispatch('submit')}
  use:queryEditor
  class="query-box"
  method="GET">
  <button type="submit" data-key="Ctrl/Cmd+Enter">{_('Submit')}</button>
</form>
