<script>
  import { initReadonlyQueryEditor } from "../codemirror/setup";

  /** @type {string} */
  export let value;

  const [, useEditor] = initReadonlyQueryEditor(value);
</script>

<pre use:useEditor />
