<!--
  @component
   A modal dialog.

   This uses a native `<dialog>`, opened with `.showModal()`. The `shown` prop is
   the source of truth - all close requests (Escape, a click on the backdrop, the
   close button) are routed through `close_handler`, which needs to update the
   state that `shown` is derived from.
-->
<script lang="ts">
  import type { Snippet } from "svelte";
  import type { Attachment } from "svelte/attachments";

  import { router } from "../router.ts";

  interface Props {
    /** Whether the modal should be shown. */
    shown: boolean;
    /** Selector for the element to focus - defaults to the first focusable one. */
    focus?: string;
    /** Handler to close the modal - defaults to clearing the URL hash. */
    close_handler?: () => void;
    children: Snippet;
  }

  let {
    shown,
    focus,
    close_handler = router.close_overlay,
    children,
  }: Props = $props();

  /** Open the dialog and focus the requested element. */
  const modal: Attachment<HTMLDialogElement> = (el) => {
    el.showModal();
    // The dialog focuses its first focusable child by default, override this here.
    const focus_el = focus != null ? el.querySelector(focus) : null;
    if (focus_el instanceof HTMLElement) {
      focus_el.focus();
    }

    // Leave the top layer and restore focus before the element is removed.
    return () => {
      el.close();
    };
  };

  /** Whether the mouse was pressed on the dialog itself, i.e. on the backdrop. */
  let pressed_on_backdrop = false;
</script>

{#if shown}
  <dialog
    {@attach modal}
    oncancel={(event) => {
      // Do not let the browser close the dialog directly - the state that
      // `shown` is derived from is the source of truth.
      event.preventDefault();
      close_handler();
    }}
    onmousedown={(event) => {
      pressed_on_backdrop =
        event.button === 0 && event.target === event.currentTarget;
    }}
    onmouseup={(event) => {
      // The dialog covers the whole viewport and `.content` is the visible box,
      // so any event targeting the dialog itself landed next to the modal.
      // Requiring the mouse to have been pressed there as well avoids closing
      // when a text selection is dragged out of (or into) the modal.
      if (pressed_on_backdrop && event.target === event.currentTarget) {
        close_handler();
      }
      pressed_on_backdrop = false;
    }}
  >
    <div class="content">
      {@render children()}
      <button type="button" class="muted close" onclick={close_handler}>
        x
      </button>
    </div>
  </dialog>
{/if}

<style>
  dialog {
    /* Cover the whole viewport - the browser default sizes and centres the
       dialog to fit its contents. `.content` is the visible box, so that the
       autocomplete dropdowns can overflow it instead of being clipped by the
       scroll container. */
    position: fixed;
    inset: 0;
    display: none;
    width: auto;
    max-width: none;
    height: auto;
    max-height: none;
    padding: 0;
    margin: 0;
    overflow: auto;
    color: inherit;
    background: none;
    border: 0;

    &[open] {
      display: flex;
      align-items: start;
      justify-content: center;
    }

    &::backdrop {
      background: var(--overlay-wrapper-background);
    }

    .content {
      position: relative;
      display: flex;
      width: 100%;
      max-width: 767px;
      padding: 1em;
      margin: 10vh 0.5em 0.5em;
      background: var(--background);
      box-shadow: var(--box-shadow-overlay);
    }

    .close {
      position: absolute;
      top: 1em;
      right: 1em;
      line-height: 1em;
    }

    .content :global(form),
    .content > :global(div) {
      width: 100%;
    }
  }

  @media (width <= 767px) {
    :global(body:has(dialog[open])) {
      overflow: hidden;
    }

    dialog {
      /* Show the modal full-screen on mobile. */
      &::backdrop {
        /* Ensure that modal overflow gets a solid background. */
        background: var(--background);
      }

      .content {
        height: 100%;
        margin: 0;
        box-shadow: unset;
      }
    }
  }
</style>
