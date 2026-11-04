import type { Attachment } from "svelte/attachments";

export interface TimedClickDetail {
  /** Whether the press duration reached or exceeded the threshold. */
  isLong: boolean;
  /** Duration of the press in milliseconds. */
  duration: number;
  /** The native PointerEvent that triggered the release. */
  originalEvent: PointerEvent;
}

/**
 * Svelte attachment to handle duration-based click events.
 *
 * Emits an `ontimedclick` CustomEvent containing the press duration and an
 * `isLong` boolean flag when the user releases a primary pointer press.
 */
export const timedclick = (threshold = 500): Attachment<HTMLElement> => {
  return (node) => {
    let startTime = 0;

    function handle_pointer_down(event: PointerEvent): void {
      if (event.button !== 0) {
        return;
      }
      startTime = Date.now();
    }

    function handle_pointer_up(event: PointerEvent): void {
      if (!startTime) {
        return;
      }

      const duration = Date.now() - startTime;
      const isLong = duration >= threshold;
      startTime = 0;

      node.dispatchEvent(
        new CustomEvent<TimedClickDetail>("timedclick", {
          detail: { isLong, duration, originalEvent: event },
        }),
      );
    }

    function handle_reset(): void {
      startTime = 0;
    }

    node.addEventListener("pointerdown", handle_pointer_down);
    node.addEventListener("pointerup", handle_pointer_up);
    node.addEventListener("pointercancel", handle_reset);
    node.addEventListener("pointerleave", handle_reset);

    return () => {
      node.removeEventListener("pointerdown", handle_pointer_down);
      node.removeEventListener("pointerup", handle_pointer_up);
      node.removeEventListener("pointercancel", handle_reset);
      node.removeEventListener("pointerleave", handle_reset);
    };
  };
};
