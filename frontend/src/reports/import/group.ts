import { type Entry, Transaction } from "../../entries/index.ts";
import { _ } from "../../i18n.ts";

/** The available groupings for the entries in the import dialog. */
export type ImportGrouping = "status" | "accounts" | "payee";

/** Get the label of the group for an entry. */
function group_label(entry: Entry, grouping: ImportGrouping): string {
  if (grouping === "status") {
    return entry.is_duplicate() ? _("Duplicates") : _("To import");
  }
  if (!(entry instanceof Transaction)) {
    return entry.t;
  }
  if (grouping === "accounts") {
    const accounts = new Set(entry.postings.map((p) => p.account));
    return `${_("Accounts")}: ${[...accounts]
      .filter((a) => a)
      .sort()
      .join(", ")}`;
  }
  return `${_("Payee")}: '${entry.payee}'`;
}

/**
 * Group the entries.
 *
 * Indices into the entries array are returned to allow updating entries.
 * Groups are in the order of their first entry, except for the status
 * grouping, which lists the entries to import first.
 */
export function group_entries(
  entries: readonly Entry[],
  grouping: ImportGrouping,
): [label: string, indices: number[]][] {
  const groups = new Map<string, number[]>();
  if (grouping === "status") {
    groups.set(_("To import"), []);
  }
  entries.forEach((entry, index) => {
    const label = group_label(entry, grouping);
    const group = groups.get(label);
    if (group) {
      group.push(index);
    } else {
      groups.set(label, [index]);
    }
  });
  return [...groups].filter(([, indices]) => indices.length > 0);
}
