import { log_error } from "./log.ts";

export class CopyableText extends HTMLElement {
  constructor() {
    super();

    this.addEventListener("click", (event) => {
      const text = this.getAttribute("data-clipboard-text");
      if (text != null) {
        navigator.clipboard.writeText(text).catch(log_error);
      }
      event.stopPropagation();
    });
  }
}
