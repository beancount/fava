import { _ } from "../../i18n";
import { DatalessRoute } from "../route";
import ErrorsSvelte from "./Errors.svelte";

export const errors = new DatalessRoute("errors", ErrorsSvelte, () =>
  _("Errors"),
);
