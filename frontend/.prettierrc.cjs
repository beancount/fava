/** @type {import("prettier").Options} */
const config = {
  plugins: [require.resolve("prettier-plugin-svelte")],
  proseWrap: "always",
  overrides: [
    {
      files: ["tsconfig.json"],
      options: {
        trailingComma: "none",
      },
    },
  ],
};

module.exports = config;
