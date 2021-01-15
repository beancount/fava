<script>
  import { closeOverlay } from "../stores";

  export let shown = false;
  export let closeHandler = closeOverlay;
</script>

<div class:shown class="overlay">
  <div class="background" on:click={closeHandler} />
  <div class="content">
    <button type="button" class="muted close" on:click={closeHandler}>x</button>
    <slot />
  </div>
</div>

<style>
  .background {
    position: fixed;
    width: 100%;
    height: 100%;
    cursor: pointer;
    background: var(--overlay-wrapper-background);
  }

  .overlay {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: var(--z-index-overlay);
    display: none;
  }

  .overlay.shown {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .close {
    position: absolute;
    top: 1em;
    right: 1em;
    margin: 0;
    color: var(--color-text-lighter);
  }

  .content {
    position: relative;
    display: flex;
    width: 100%;
    max-width: 767px;
    max-height: 100%;
    padding: 1em;
    margin: 0.5em;
    background: var(--color-background);
    box-shadow: 0 0 20px var(--overlay-wrapper-background);
  }
  .content :global(form),
  .content > :global(div) {
    width: 100%;
  }
</style>
