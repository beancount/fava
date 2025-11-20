import { get_options } from "../../api/index.ts";
import { _ } from "../../i18n.ts";
import { Route } from "../route.ts";
import OptionsSvelte from "./Options.svelte";

export interface OptionsReportProps {
  fava_options: Record<string, string>;
  beancount_options: Record<string, string>;
}

export const options = new Route<OptionsReportProps>(
  "options",
  OptionsSvelte,
  async () => get_options(),
  () => _("Options"),
);
