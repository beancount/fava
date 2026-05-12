import { get as store_get } from "svelte/store";

import { get_journal_page } from "../../api/index.ts";
import { _ } from "../../i18n.ts";
import { fragment_from_string } from "../../lib/dom.ts";
import { shallow_equal } from "../../lib/equals.ts";
import { log_error } from "../../log.ts";
import { notify_err } from "../../notifications.ts";
import { getURLFilters } from "../../stores/filters.ts";
import { journal_sort, type JournalSort } from "../../stores/journal.ts";
import { Route } from "../route.ts";
import Journal from "./Journal.svelte";

export interface JournalReportProps {
  journal: DocumentFragment;
  initial_sort: JournalSort;
  load_page: (page: number) => Promise<DocumentFragment | null>;
  total_pages: number;
}

export const journal = new Route<JournalReportProps>(
  "journal",
  Journal,
  async (url: URL) => {
    const filters = getURLFilters(url);
    const $journal_sort = store_get(journal_sort);
    const order = shallow_equal($journal_sort, ["date", "asc"])
      ? "asc"
      : "desc";
    const { journal, total_pages } = await get_journal_page({
      ...filters,
      page: 1,
      order,
    });

    let error_shown = false;
    const load_page = async (page: number) => {
      return get_journal_page({ ...filters, page, order }).then(
        (res) => fragment_from_string(res.journal),
        (error: unknown) => {
          log_error(`Failed to fetch page ${page.toString()}`, error);
          if (!error_shown) {
            notify_err(new Error("Failed to fetch some journal pages"));
            error_shown = true;
          }
          return null;
        },
      );
    };

    return {
      journal: fragment_from_string(journal),
      initial_sort: ["date", order],
      load_page,
      total_pages,
    };
  },
  () => _("Journal"),
);
