<script>
  import { initReadonlyQueryEditor } from "../codemirror/setup";

  /** @type {string} */
  export let value;

  /**
   * @param {HTMLElement} el
   */
  function queryEditor(el) {
    const editor = initReadonlyQueryEditor(value);
    el.appendChild(editor.dom);
  }
</script>

<pre use:queryEditor />
