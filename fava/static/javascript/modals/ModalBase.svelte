<div class:shown class="overlay">
  <div class="overlay-background" on:click="{closeOverlay}"></div>
  <div class="overlay-content">
    <button type="button" class="muted close-overlay" on:click="{closeOverlay}">
      x
    </button>
    <slot> </slot>
  </div>
</div>
<script>
  import e from "../events";
  import { _ } from "../helpers";
  import { closeOverlay } from "../stores";

  export let shown = false;
</script>
