<script>
  import { baseURL } from "../stores/url";

  /** @type {string} */
  export let filename;
</script>

<style>
  object {
    width: 100%;
    height: 100%;
  }
</style>

<object title={filename} data={`${$baseURL}document/?filename=${filename}`} />
