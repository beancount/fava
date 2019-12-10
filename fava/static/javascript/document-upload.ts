/*
 * File uploads via Drag and Drop on elements with class "droptarget"
 * and attribute "data-account-name"
 */

import { writable, Writable } from "svelte/store";

import { todayAsString } from "./format";
import { delegate, _ } from "./helpers";
import { favaAPI } from "./stores";
import { notify } from "./notifications";

function dragover(event: DragEvent, closestTarget: HTMLElement) {
  closestTarget.classList.add("dragover");
  event.preventDefault();
}
delegate(document, "dragenter", ".droptarget", dragover);
delegate(document, "dragover", ".droptarget", dragover);

function dragleave(event: DragEvent, closestTarget: HTMLElement) {
  closestTarget.classList.remove("dragover");
  event.preventDefault();
}
delegate(document, "dragleave", ".droptarget", dragleave);

/* Stores that the Svelte component accesses. */
export const account = writable("");
export const hash = writable("");
export const files: Writable<{
  dataTransferFile: File;
  name: string;
}[]> = writable([]);

function drop(event: DragEvent, target: HTMLElement) {
  target.classList.remove("dragover");
  event.preventDefault();
  event.stopPropagation();

  if (!event.dataTransfer || !event.dataTransfer.files.length) {
    return;
  }
  if (!favaAPI.options.documents.length) {
    notify(
      _('You need to set the "documents" Beancount option for file uploads.'),
      "error"
    );
    return;
  }

  const dateAttribute = target.getAttribute("data-entry-date");
  const entryDate = dateAttribute || todayAsString();
  account.set(target.getAttribute("data-account-name") || "");
  hash.set(target.getAttribute("data-entry") || "");

  const uploadedFiles: { dataTransferFile: File; name: string }[] = [];
  for (const dataTransferFile of event.dataTransfer.files) {
    let { name } = dataTransferFile;

    if (!/^\d{4}-\d{2}-\d{2}/.test(name)) {
      name = `${entryDate} ${name}`;
    }

    uploadedFiles.push({
      dataTransferFile,
      name,
    });
  }
  files.set(uploadedFiles);
}

delegate(document, "drop", ".droptarget", drop);
