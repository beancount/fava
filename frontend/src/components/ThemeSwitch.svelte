<script lang="ts">
  import { themeStore } from "../stores/theme";

  const icons = {
    light: {
      viewBox: "0 0 24 24",
      path: "M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1z",
    },
    dark: {
      viewBox: "0 0 24 24",
      path: "M9.37 5.51A7.35 7.35 0 0 0 9.1 7.5c0 4.08 3.32 7.4 7.4 7.4.68 0 1.35-.09 1.99-.27A7.014 7.014 0 0 1 12 19c-3.86 0-7-3.14-7-7 0-2.93 1.81-5.45 4.37-6.49zM12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z",
    },
  };
</script>

<div class="theme-switch">
  {#each [...themeStore.values()] as [option, name]}
    <button
      type="button"
      class="theme-button"
      class:active={$themeStore === option}
      on:click={() => {
        themeStore.set(option);
      }}
      title={name}
    >
      <svg
        viewBox={icons[option].viewBox}
        width="16"
        height="16"
        aria-hidden="true"
      >
        <path fill="currentColor" d={icons[option].path} />
      </svg>
    </button>
  {/each}
</div>

<style>
  .theme-switch {
    display: flex;
    gap: 2px;
    padding: 3px;
    margin-right: 0.5em;
    background: var(--background-darker);
    border-radius: 8px;
  }

  .theme-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    padding: 0;
    color: var(--text-color-lighter);
    cursor: pointer;
    background: transparent;
    border: none;
    border-radius: 6px;
    transition: all 0.2s ease;
  }

  .theme-button:hover {
    color: var(--text-color);
    background: var(--background);
  }

  .theme-button.active {
    color: var(--header-color);
    background: var(--header-background);
  }

  /* Ensure SVG icons inherit color properly */
  .theme-button svg {
    width: 18px;
    height: 18px;
  }

  @media (width <= 768px) {
    .theme-button {
      width: 28px;
      height: 28px;
    }

    .theme-button svg {
      width: 16px;
      height: 16px;
    }
  }
</style>
