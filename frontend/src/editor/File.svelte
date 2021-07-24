<script>
  import { urlFor } from "../helpers";

  export let file;
  /** @type {string} */
  export let file_path;
</script>

<span class:selected={file.path === file_path}>
  <a href={urlFor("editor", { file_path: file.path })}>{file.name}</a>
</span>

<style>
  .selected::before {
    content: "›";
  }

  span {
    padding: 2px 10px;
    cursor: pointer;
  }
</style>
