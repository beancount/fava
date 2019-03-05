<script>
  import { onMount } from "svelte";

  import { delegate } from "../helpers";

  import AddTransaction from "./AddTransaction.svelte";
  import Context from "./Context.svelte";
  import DocumentUpload from "./DocumentUpload.svelte";
  import Export from "./Export.svelte";
  import Extract from "./Extract.svelte";

  let documentUploadModal;
  // File uploads via Drag and Drop on elements with class "droptarget" and
  // attribute "data-account-name"
  onMount(() => {
    delegate(document, "dragenter", ".droptarget", (event, closestTarget) => {
      closestTarget.classList.add("dragover");
      event.preventDefault();
    });

    delegate(document, "dragover", ".droptarget", (event, closestTarget) => {
      closestTarget.classList.add("dragover");
      event.preventDefault();
    });

    delegate(document, "dragleave", ".droptarget", (event, closestTarget) => {
      closestTarget.classList.remove("dragover");
      event.preventDefault();
    });

    delegate(document, "drop", ".droptarget", (event, closestTarget) => {
      closestTarget.classList.remove("dragover");
      event.preventDefault();
      event.stopPropagation();
      documentUploadModal.handleDrop(event, closestTarget);
    });
  });
</script>
<AddTransaction />
<Context />
<DocumentUpload bind:this="{documentUploadModal}" />
<Export />
<Extract />
