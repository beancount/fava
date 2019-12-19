import { select, delegate } from "./helpers";

/*
 * Show a notification containing the given `msg` text and having class `cls`.
 * The notification is automatically removed after 5 seconds and on click
 * `callback` is called.
 *
 * @param {string} msg - The message to diplay
 * @param {string} cls - The message type.
 * @param {function} callback - The callback to execute on click..
 */
export function notify(msg: string, cls = "info", callback?: Function) {
  const notification = document.createElement("li");
  notification.classList.add(cls);
  notification.appendChild(document.createTextNode(msg));
  const notificationList = select("#notifications");
  if (!notificationList) {
    throw new Error();
  }
  notificationList.append(notification);
  notification.addEventListener("click", () => {
    notification.remove();
    if (callback) {
      callback();
    }
  });
  setTimeout(() => {
    notification.remove();
  }, 5000);
}

delegate(select("#notifications"), "click", "li", (event, closest) => {
  closest.remove();
});
