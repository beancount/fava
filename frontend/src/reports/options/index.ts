import { get } from "../../api";
import { _ } from "../../i18n";
import { Route } from "../route";
import OptionsSvelte from "./Options.svelte";

export const options = new Route(
  "options",
  OptionsSvelte,
  async () => get("options"),
  () => _("Options"),
);
