<script lang="ts">
  import { writable } from "svelte/store";

  import { _ } from "../../i18n";

  export const theme = writable(localStorage.getItem("theme") ?? "auto");

  theme.subscribe((value) => {
    if (value === "auto") {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", value);
    }
    localStorage.setItem("theme", value);
  });

  function handleThemeChange(event: Event) {
    const selectedTheme = (event.target as HTMLButtonElement).value;
    theme.set(selectedTheme);
  }
</script>

<div class="theme-toggle">
  <button
    type="button"
    class="theme-button"
    value="auto"
    on:click={handleThemeChange}
    aria-pressed={$theme === "auto"}
  >
    💻 {_("System")}
  </button>

  <button
    type="button"
    class="theme-button"
    value="light"
    on:click={handleThemeChange}
    aria-pressed={$theme === "light"}
  >
    ☀️ {_("Light")}
  </button>

  <button
    type="button"
    class="theme-button"
    value="dark"
    on:click={handleThemeChange}
    aria-pressed={$theme === "dark"}
  >
    🌙 {_("Dark")}
  </button>
</div>

<style>
  .theme-toggle {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
    margin-bottom: 1.5rem;
  }

  .theme-button {
    display: inline-block;
    width: 8rem;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    color: var(--text-color);
    text-align: left;
    cursor: pointer;
    background-color: var(--background);
    border: 1px solid var(--border);
    transition:
      background-color 0.2s,
      color 0.2s;
  }

  .theme-button:hover {
    color: var(--link-color);
    background-color: var(--background-darker);
  }

  .theme-button[aria-pressed="true"] {
    font-weight: bold;
    color: #fff;
    background-color: var(--link-color);
  }
</style>
