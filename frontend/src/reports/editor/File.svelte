<script lang="ts">
  import type { FileNode } from "./treeview";

  export let file: FileNode;
  export let file_path: string;
</script>

<span class:selected={file.path === file_path}>
  <button type="button" on:click={file.action}>
    {file.name}
  </button>
</span>

<style>
  .selected::before {
    content: "›";
  }

  span {
    padding: 2px 0;
    cursor: pointer;
  }

  button {
    display: contents;
    color: blue;
  }
</style>
