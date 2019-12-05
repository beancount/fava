<script>
  import { createEventDispatcher } from "svelte";

  import { _ } from "../helpers";

  import AccountInput from "./AccountInput.svelte";

  export let posting;
  export let index;
  export let suggestions;

  const dispatch = createEventDispatcher();

  let drag = false;
  let draggable = true;
  function mousemove(event) {
    draggable = event.target.nodeName !== "INPUT";
  }
  function dragstart(event) {
    event.dataTransfer.setData("fava/posting", index);
  }
  function dragenter(event) {
    if (event.dataTransfer.types.includes("fava/posting")) {
      event.preventDefault();
      drag = true;
    }
  }
  function dragleave() {
    drag = false;
  }
  function drop(event) {
    const from = event.dataTransfer.getData("fava/posting");
    if (from) {
      dispatch("move", { from: +from, to: index });
      drag = false;
    }
  }
</script>

<style>
  .drag {
    box-shadow: 0 0 5px var(--color-text);
  }
</style>

<div
  class="fieldset posting"
  class:drag
  {draggable}
  on:mousemove={mousemove}
  on:dragstart={dragstart}
  on:dragenter={dragenter}
  on:dragover={dragenter}
  on:dragleave={dragleave}
  on:drop|preventDefault={drop}>
  <button
    class="muted round remove-fieldset"
    on:click={() => dispatch('remove')}
    type="button"
    tabindex="-1">
    ×
  </button>
  <AccountInput bind:value={posting.account} {suggestions} />
  <input
    type="text"
    class="amount"
    placeholder={_('Amount')}
    bind:value={posting.amount} />
  <button
    class="muted round add-row"
    type="button"
    on:click={() => dispatch('add')}
    title={_('Add posting')}>
    +
  </button>
</div>
