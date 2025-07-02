import { _ } from "../i18n";
import { localStorageSyncedStore } from "../lib/store";
import { constants, type ValidationT } from "../lib/validation";

const color_scheme_validator = constants("light dark", "dark", "light");

/** The currently selected colorScheme. */
export const color_scheme = localStorageSyncedStore<
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

/** Set the color scheme on store changes. */
export function init_color_scheme(): void {
  color_scheme.subscribe(($theme) => {
    document.documentElement.style.colorScheme = $theme;
  });
}
