/** @type {import("prettier").Options} */
const config = {
  plugins: [import.meta.resolve("prettier-plugin-svelte")],
  proseWrap: "always",
};

export default config;
