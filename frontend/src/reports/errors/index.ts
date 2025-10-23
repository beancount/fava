import { _ } from "../../i18n.ts";
import { DatalessRoute } from "../route.ts";
import ErrorsSvelte from "./Errors.svelte";

export const errors = new DatalessRoute("errors", ErrorsSvelte, () =>
  _("Errors"),
);
