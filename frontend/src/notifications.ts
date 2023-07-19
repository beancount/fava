import { log_error } from "./log";

/** The notification list div, lazily created. */
const notificationList = (() => {
  let value: HTMLDivElement | null = null;
  return () => {
    if (value === null) {
      value = document.createElement("div");
      value.className = "notifications";
      document.body.appendChild(value);
    }
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
  // eslint-disable-next-line default-param-last
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
 * Notify the user about an error and log to console.
 */
export function notify_err(error: unknown, msg: (e: Error) => string): void {
  if (error instanceof Error) {
    notify(msg(error), "error");
  }
  log_error(error);
}
