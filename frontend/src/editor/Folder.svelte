<script>
  import File from "./File.svelte";

  export let expanded = false;
  export let folder;
  /** @type {string} */
  export let file_path;

  function toggle() {
    expanded = !expanded;
  }
</script>

<style>
  span {
    padding: 2px 10px;
    font-weight: bold;
    cursor: pointer;
  }

  .collapse::before {
    content: "+";
  }

  ul {
    padding: 0.2em 0 0 0.5em;
    margin: 0 0 0 0.5em;
    list-style: none;
    border-left: 1px solid #eee;
  }

  li {
    padding: 0.2em 0;
  }
</style>

<span class:collapse={!expanded} on:click={toggle}>{folder.name}</span>

{#if expanded}
  <ul>
    {#each folder.subfiles as file}
      <li>
        <File {file} {file_path} />
      </li>
    {/each}
    {#each folder.subfolders as subfolder}
      <li>
        <svelte:self folder={subfolder} {file_path} expanded />
      </li>
    {/each}
  </ul>
{/if}
