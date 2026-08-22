import { _ } from "../i18n.ts";
import { local_storage_synced_store } from "../lib/store.ts";
import { constants, type ValidationT } from "../lib/validation.ts";

const color_scheme_validator = constants("light dark", "dark", "light");

/** The currently selected colorScheme. */
export const color_scheme = local_storage_synced_store<
  ValidationT<typeof color_scheme_validator>
>(
  "theme",
  color_scheme_validator,
  () => "light dark",
  () => [
    ["light dark", `⚙️ ${_("System")}`],
    ["dark", `🌙 ${_("Dark")}`],
    ["light", `☀️ ${_("Light")}`],
  ],
);

/** Set the color scheme on store changes (see style.css). */
export function init_color_scheme(): void {
  color_scheme.subscribe(($theme) => {
    document.documentElement.dataset.colorScheme = $theme;
  });
}
