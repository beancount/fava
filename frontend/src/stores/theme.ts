import { constants } from "../lib/validation";
import { localStorageSyncedStore } from "../lib/store";
import type { ValidationT } from "../lib/validation";

const theme_validator = constants("light", "dark");
type Theme = ValidationT<typeof theme_validator>;

export const themeStore = localStorageSyncedStore<Theme>(
  "theme",
  theme_validator,
  () => "dark", // Set dark as default
  () => [
    ["light", "Light"],
    ["dark", "Dark"],
  ],
);

// Apply theme class to document
themeStore.subscribe((theme: Theme) => {
  if (theme === "light") {
    document.documentElement.classList.remove("dark-theme");
    document.documentElement.classList.add("light-theme");
  } else {
    document.documentElement.classList.remove("light-theme");
    document.documentElement.classList.add("dark-theme");
  }
});
