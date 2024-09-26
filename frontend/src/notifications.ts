import { errorWithCauses } from "./lib/errors";
import { log_error } from "./log";

/** The notification list div, lazily created. */
const notificationList = (() => {
  let value: HTMLDivElement | null = null;
  return () => {
    if (value === null) {
      value = document.createElement("div");
      value.className = "notifications";
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
 * @param msg - The message to diplay
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
  notificationList().append(notification);
  notification.addEventListener("click", () => {
    notification.remove();
    callback?.();
  });
  setTimeout(() => {
    notification.remove();
  }, 5000);
}

/**
 * Notify the user about an warning and log to console.
 */
export function notify_warn(msg: string): void {
  notify(msg, "warning");

  console.warn(msg);
}

/**
 * Notify the user about an error and log to console.
 */
export function notify_err(
  error: unknown,
  msg: (e: Error) => string = errorWithCauses,
): void {
  if (error instanceof Error) {
    notify(msg(error), "error");
  }
  log_error(error);
}
