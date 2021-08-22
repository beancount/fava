/*
 * File uploads via Drag and Drop on elements with class "droptarget"
 * and attribute "data-account-name"
 */

import type { Writable } from "svelte/store";
import { writable } from "svelte/store";

import { put } from "./api";
import { todayAsString } from "./format";
import { delegate } from "./lib/events";
import { basename, documentHasAccount } from "./lib/paths";
import { notify } from "./notifications";

function dragover(event: DragEvent, closestTarget: HTMLElement): void {
  if (
    event.dataTransfer &&
    (event.dataTransfer.types.includes("Files") ||
      event.dataTransfer.types.includes("text/uri-list"))
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
export const files: Writable<
  {
    dataTransferFile: File;
    name: string;
  }[]
> = writable([]);

function drop(event: DragEvent, target: HTMLElement): void {
  target.classList.remove("dragover");
  event.preventDefault();
  event.stopPropagation();
  if (!event.dataTransfer) {
    return;
  }

  const url = event.dataTransfer.getData("URL");
  if (url) {
    let filename = new URL(url).searchParams.get("filename");
    const acc = target.getAttribute("data-account-name");
    if (acc && filename && documentHasAccount(filename, acc)) {
      filename = basename(filename);
    }
    const entry_hash = target.getAttribute("data-entry");
    if (filename && entry_hash) {
      put("attach_document", { filename, entry_hash }).then(
        (response) => {
          notify(response);
        },
        (error) => {
          notify(error, "error");
        }
      );
    }
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
