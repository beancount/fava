import { get } from "../../api";
import { _ } from "../../i18n";
import { Route } from "../route";
import OptionsSvelte from "./Options.svelte";

export interface OptionsReportProps {
  fava_options: Record<string, string>;
  beancount_options: Record<string, string>;
}

export const options = new Route<OptionsReportProps>(
  "options",
  OptionsSvelte,
  async () => get("options"),
  () => _("Options"),
);
