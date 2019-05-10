<script>
  import { onMount } from "svelte";

  import { urlHash } from "../stores";

  import ModalBase from "./ModalBase.svelte";

  let content = "";
  $: shown = $urlHash === "export";

  onMount(() => {
    const template = document.querySelector("#export-overlay-content");
    content = template.innerHTML;
  });
</script>

<ModalBase {shown}>
  <div>
    {@html content}
  </div>
</ModalBase>
