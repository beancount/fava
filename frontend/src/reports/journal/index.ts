import { get } from "../../api";
import type { Entry } from "../../entries";
import { _ } from "../../i18n";
import { getURLFilters } from "../../stores/filters";
import { Route } from "../route";
import Journal from "./Journal.svelte";

export interface JournalProps {
  entries: Entry[];
}

export const journal = new Route<JournalProps>(
  "journal",
  Journal,
  async (url) => {
    const entries = await get("journal", getURLFilters(url));
    return { entries };
  },
  () => _("Journal"),
);
