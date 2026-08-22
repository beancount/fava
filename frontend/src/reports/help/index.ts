import { get_help } from "../../api/index.ts";
import { get_url_path } from "../../helpers.ts";
import { _ } from "../../i18n.ts";
import { Route } from "../route.ts";
import Help from "./Help.svelte";

export interface HelpReportProps {
  /** Slug of the currently shown help page. */
  page_slug: string;
  /** The rendered HTML of the currently shown help page. */
  html: string;
  /** All help pages. */
  pages: [slug: string, title: string][];
}

/**
 * Get the slug of the help page that the given URL should show.
 */
function get_page_slug(url: URL): string {
  const [, page_slug] = get_url_path(url).unwrap().split("/");
  return page_slug != null && page_slug !== "" ? page_slug : "_index";
}

export const help = new Route<HelpReportProps>(
  "help",
  Help,
  async (url) => {
    const page_slug = get_page_slug(url);
    const { html, pages } = await get_help({ page_slug });

    return { page_slug, html, pages };
  },
  ({ pages, page_slug }) => {
    const title = pages.find(([s]) => s === page_slug)?.[1];
    return title != null ? `${_("Help")} - ${title}` : _("Help");
  },
);
