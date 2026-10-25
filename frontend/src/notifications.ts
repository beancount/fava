import { error_with_causes } from "./lib/errors.ts";
import { log_error } from "./log.ts";

/** The notification list div, lazily created. */
const notificationList = (() => {
  let value: HTMLDivElement | null = null;
  return () => {
    if (value == null) {
      value = document.createElement("div");
      value.className = "notifications";
      // Show as a popover so that it is in the top layer like modal dialogs.
      value.popover = "manual";
      value.style.right = "10px";
      document.body.appendChild(value);
    }
    // always update the distance to top to account for the current header height
    const headerHeight =
      document.querySelector("header")?.getBoundingClientRect().height ?? 50;
    value.style.top = `${(headerHeight + 10).toString()}px`;
    return value;
  };
})();

type NotificationType = "info" | "warning" | "error";

/**
 * Show a notification containing the given `msg` text and having class `cls`.
 * The notification is automatically removed after 5 seconds and on click
 * `callback` is called.
 *
 * @param msg - The message to display
 * @param cls - The message type.
 * @param callback - The callback to execute on click..
 */
export function notify(
  msg: string,
  cls: NotificationType = "info",
  callback?: () => void,
): void {
  const notification = document.createElement("li");
  notification.classList.add(cls);
  notification.appendChild(document.createTextNode(msg));
  const list = notificationList();
  list.append(notification);
  // (Re-)show to move it to the top of the top layer, above any open dialogs.
  list.hidePopover();
  list.showPopover();
  notification.addEventListener("click", () => {
    notification.remove();
    callback?.();
  });
  setTimeout(() => {
    notification.remove();
  }, 5000);
}

/**
 * Notify the user about an error and log to console.
 */
export function notify_err(
  error: unknown,
  msg: (e: Error) => string = error_with_causes,
): void {
  if (error instanceof Error) {
    notify(msg(error), "error");
  }
  log_error(error);
}
