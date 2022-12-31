<script lang="ts">
  import File from "./File.svelte";
  import type { FolderNode } from "./treeview";

  export let force_expand = false;
  export let folder: FolderNode;
  export let file_path: string;
</script>

<div class:force-expand={force_expand}>
  <span>{folder.name}</span>

  <ul>
    {#each folder.subfiles as file}
      <li>
        <File {file} {file_path} />
      </li>
    {/each}
    {#each folder.subfolders as subfolder}
      <li>
        <svelte:self folder={subfolder} {file_path} />
      </li>
    {/each}
  </ul>
</div>

<style>
  span {
    padding: 2px 0;
    font-weight: bold;
    cursor: pointer;
  }

  ul {
    padding: 0.2em 0 0 1em;
    margin: 0 0 0 0.27em;
    list-style: none;
  }

  li {
    padding: 0.2em 0;
  }

  div {
    display: inline-block;
  }

  div > ul {
    display: none;
  }

  div:hover > ul,
  div.force-expand > ul {
    display: block;
  }

  div:not(:hover, .force-expand) > span::before {
    font-family: monospace;
    content: "+";
  }

  div:hover > span::before,
  div.force-expand > span::before {
    font-family: monospace;
    content: "-";
  }
</style>
