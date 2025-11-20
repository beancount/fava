import { _ } from "../../i18n.ts";
import { DatalessRoute } from "../route.ts";
import QuerySvelte from "./Query.svelte";

export const query = new DatalessRoute("query", QuerySvelte, () => _("Query"));
