<!--
  @component
   A modal dialog.

   This tries to follow https://www.w3.org/TR/wai-aria-practices-1.1/#dialog_modal.
-->
<script lang="ts">
  import type { Action } from "svelte/action";

  import { attemptFocus, getFocusableElements } from "../lib/focus";
  import { closeOverlay } from "../stores/url";

  export let shown = false;
  export let focus: string | undefined = undefined;
  export let closeHandler = closeOverlay;

  /**
   * A Svelte action to handle focus within a modal.
   */
  const handleFocus: Action = (el) => {
    const keydown = (ev: KeyboardEvent) => {
      if (ev.key === "Tab") {
        const focusable = getFocusableElements(el);
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (ev.shiftKey && document.activeElement === first && last) {
          ev.preventDefault();
          attemptFocus(last);
        } else if (!ev.shiftKey && document.activeElement === last && first) {
          ev.preventDefault();
          attemptFocus(first);
        }
      } else if (ev.key === "Escape") {
        ev.preventDefault();
        closeHandler();
      }
    };
    document.addEventListener("keydown", keydown);

    const selectorFocusEl = focus != null ? el.querySelector(focus) : undefined;
    const focusEl = selectorFocusEl ?? getFocusableElements(el)[0];
    if (focusEl) {
      attemptFocus(focusEl);
    }

    return {
      destroy: () => {
        document.removeEventListener("keydown", keydown);
      },
    };
  };
</script>

{#if shown}
  <div class="overlay">
    <div class="background" on:click={closeHandler} aria-hidden="true" />
    <div class="content" use:handleFocus role="dialog" aria-modal="true">
      <slot />
      <button type="button" class="muted close" on:click={closeHandler}
        >x</button
      >
    </div>
  </div>
{/if}

<style>
  :global(body):has(.overlay) {
    overflow: hidden;
  }

  .background {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    cursor: pointer;
    background: var(--overlay-wrapper-background);
  }

  .overlay {
    position: fixed;
    inset: 0;
    z-index: var(--z-index-overlay);
    display: flex;
    align-items: start;
    justify-content: center;
    width: 100vw;
    height: 100vh;
    overflow: auto;
  }

  .content {
    position: relative;
    display: flex;
    width: 100%;
    max-width: 767px;
    padding: 1em;
    margin: 0.5em;
    margin-top: 10vh;
    background: var(--background);
    box-shadow: var(--box-shadow-overlay);
  }

  .close {
    position: absolute;
    top: 1em;
    right: 1em;
    width: 2em;
    height: 2em;
    margin: 0;
    line-height: 1em;
    color: var(--text-color-lighter);
  }

  .content :global(form),
  .content > :global(div) {
    width: 100%;
  }

  @media (width <= 767px) {
    /* Show the modal full-screen on mobile. */
    .overlay {
      height: 100%;
    }

    .background {
      /* Ensure that modal overflow gets a white background. */
      background: var(--background);
    }

    .content {
      height: 100%;
      margin: 0;
      box-shadow: unset;
    }
  }
</style>
