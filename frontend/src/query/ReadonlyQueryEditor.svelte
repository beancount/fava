<script lang="ts">
  import { initReadonlyQueryEditor } from "../codemirror/setup";

  export let value: string;

  const [, useEditor] = initReadonlyQueryEditor(value);
</script>

<pre use:useEditor />
