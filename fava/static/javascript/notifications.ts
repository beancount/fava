const notificationList = document.createElement("div");
notificationList.className = "notifications";
document.body.appendChild(notificationList);

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
  callback?: () => void
): void {
  const notification = document.createElement("li");
  notification.classList.add(cls);
  notification.appendChild(document.createTextNode(msg));
  notificationList.append(notification);
  notification.addEventListener("click", () => {
    notification.remove();
    callback?.();
  });
  setTimeout(() => {
    notification.remove();
  }, 5000);
}
