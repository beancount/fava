import e from "./events";
import { select, selectAll } from "./helpers";

// Copy the given text to the clipboard.
function copyToClipboard(text: string | null) {
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
    console.error("Unable to copy", err); // eslint-disable-line no-console
  }
  textarea.remove();
}

e.on("page-loaded", () => {
  selectAll(".status-indicator").forEach(indicator => {
    indicator.addEventListener("click", () => {
      copyToClipboard(indicator.getAttribute("data-clipboard-text"));
    });
  });

  const copyBalances = select("#copy-balances");
  if (copyBalances) {
    copyBalances.addEventListener("click", () => {
      copyToClipboard(copyBalances.getAttribute("data-clipboard-text"));
    });
  }
});
