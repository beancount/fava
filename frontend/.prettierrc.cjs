/** @type {import("prettier").Options} */
const config = {
  plugins: [require.resolve("prettier-plugin-svelte")],
  proseWrap: "always",
};

module.exports = config;
