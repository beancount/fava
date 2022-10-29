/*
 * File uploads via Drag and Drop on elements with class "droptarget"
 * and attribute "data-account-name".
 */

import type { Writable } from "svelte/store";
import { writable } from "svelte/store";

import { put } from "./api";
import { todayAsString } from "./format";
import { delegate } from "./lib/events";
import { basename, documentHasAccount } from "./lib/paths";
import { notify } from "./notifications";

/**
 * Handle a dragenter or dragover event.
 *
 * We want to allow a drop if the dragged thing is either a file that could be
 * dragged from a file manager or a URL (as dragged from a document link in Fava).
 */
function dragover(event: DragEvent, closestTarget: HTMLElement): void {
  if (
    event.dataTransfer?.types.includes("Files") ||
    event.dataTransfer?.types.includes("text/uri-list")
  ) {
    closestTarget.classList.add("dragover");
    event.preventDefault();
  }
}
delegate(document, "dragenter", ".droptarget", dragover);
delegate(document, "dragover", ".droptarget", dragover);

function dragleave(event: DragEvent, closestTarget: HTMLElement): void {
  closestTarget.classList.remove("dragover");
  event.preventDefault();
}
delegate(document, "dragleave", ".droptarget", dragleave);

/* Stores that the Svelte component accesses. */
export const account = writable("");
export const hash = writable("");

type DroppedFile = { dataTransferFile: File; name: string };
export const files: Writable<DroppedFile[]> = writable([]);

function drop(event: DragEvent, target: HTMLElement): void {
  target.classList.remove("dragover");
  event.preventDefault();
  event.stopPropagation();
  if (!event.dataTransfer) {
    return;
  }

  // Account name that the document should be attached to.
  const targetAccount = target.getAttribute("data-account-name");
  // Hash of the entry that the document should be attached to.
  const targetEntry = target.getAttribute("data-entry");

  if (event.dataTransfer.types.includes("Files")) {
    // Files are being dropped.
    const date = target.getAttribute("data-entry-date") ?? todayAsString();
    const uploadedFiles: DroppedFile[] = [];
    for (const dataTransferFile of event.dataTransfer.files) {
      let { name } = dataTransferFile;
      if (!/^\d{4}-\d{2}-\d{2}/.test(name)) {
        name = `${date} ${name}`;
      }
      uploadedFiles.push({ dataTransferFile, name });
    }
    account.set(targetAccount ?? "");
    hash.set(targetEntry ?? "");
    files.set(uploadedFiles);
  } else if (event.dataTransfer.types.includes("text/uri-list")) {
    // Links are being dropped
    const url = event.dataTransfer.getData("URL");
    // Try to extract the filename from the URL.
    let filename = new URL(url).searchParams.get("filename");
    if (filename && targetEntry) {
      if (targetAccount && documentHasAccount(filename, targetAccount)) {
        filename = basename(filename);
      }
      put("attach_document", { filename, entry_hash: targetEntry }).then(
        notify,
        (error) => {
          if (error instanceof Error) {
            notify(error.message, "error");
          }
        }
      );
    }
  }
}

delegate(document, "drop", ".droptarget", drop);
