<script lang="ts">
  import { is_loading } from "../router.ts";
</script>

<svg
  class:loading={$is_loading}
  xmlns="http://www.w3.org/2000/svg"
  width="24"
  height="24"
  viewBox="0 0 100 100"
>
  <rect width="100" height="100" rx="20" fill="#0a0a0a" />
  <text
    x="50"
    y="68"
    font-size="50"
    font-family="system-ui"
    font-weight="bold"
    text-anchor="middle"
  >
    <tspan fill="#f97316">r</tspan><tspan fill="white">f</tspan>
  </text>
</svg>

<style>
  @keyframes spinner {
    to {
      transform: rotate(360deg);
    }
  }

  .loading {
    padding: 0;
    border-top: 2px solid var(--header-color);
    border-radius: 50%;
    animation: spinner 1s linear infinite;
  }

  .loading rect,
  .loading text {
    opacity: 0;
  }

  @media print {
    svg {
      display: none;
    }
  }
</style>
