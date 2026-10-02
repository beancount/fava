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

    function handlePointerDown(event: PointerEvent): void {
      if (event.button !== 0) return;
      startTime = Date.now();
    }

    function handlePointerUp(event: PointerEvent): void {
      if (!startTime) return;

      const duration = Date.now() - startTime;
      const isLong = duration >= threshold;
      startTime = 0;

      node.dispatchEvent(
        new CustomEvent<TimedClickDetail>("timedclick", {
          detail: { isLong, duration, originalEvent: event },
        }),
      );
    }

    function handleReset(): void {
      startTime = 0;
    }

    node.addEventListener("pointerdown", handlePointerDown);
    node.addEventListener("pointerup", handlePointerUp);
    node.addEventListener("pointercancel", handleReset);
    node.addEventListener("pointerleave", handleReset);

    return () => {
      node.removeEventListener("pointerdown", handlePointerDown);
      node.removeEventListener("pointerup", handlePointerUp);
      node.removeEventListener("pointercancel", handleReset);
      node.removeEventListener("pointerleave", handleReset);
    };
  };
};
