<script>
  import { closeOverlay } from "../stores";

  export let shown = false;
  export let closeHandler = closeOverlay;
</script>

<div class:shown class="overlay">
  <div class="overlay-background" on:click={closeHandler} />
  <div class="overlay-content">
    <button type="button" class="muted close-overlay" on:click={closeHandler}>
      x
    </button>
    <slot />
  </div>
</div>
