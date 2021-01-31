import { log_error } from "./log";

/**
 * Copy the given text to the clipboard.
 */
function copyToClipboard(text: string | null): void {
  if (!text) {
    return;
  }
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.top = "0";
  textarea.style.left = "0";
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();

  try {
    document.execCommand("copy");
  } catch (err) {
    log_error(err);
  }
  textarea.remove();
}

export class CopyableText extends HTMLElement {
  constructor() {
    super();

    this.addEventListener("click", (event) => {
      copyToClipboard(this.getAttribute("data-clipboard-text"));
      event.stopPropagation();
    });
  }
}
