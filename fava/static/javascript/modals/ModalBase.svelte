<script>
  import { closeOverlay } from "../stores";

  export let shown = false;
</script>

<div class:shown class="overlay">
  <div class="overlay-background" on:click={closeOverlay} />
  <div class="overlay-content">
    <button type="button" class="muted close-overlay" on:click={closeOverlay}>
      x
    </button>
    <slot />
  </div>
</div>
