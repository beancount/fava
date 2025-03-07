import { _ } from "../../i18n";
import { DatalessRoute } from "../route";
import QuerySvelte from "./Query.svelte";

export const query = new DatalessRoute("query", QuerySvelte, () => _("Query"));
