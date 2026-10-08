import type { TimedClickDetail } from "./charts/timed-click.ts";

declare module "svelte/elements" {
  interface HTMLAttributes<T> {
    ontimedclick?: (event: CustomEvent<TimedClickDetail>) => void;
  }
}
