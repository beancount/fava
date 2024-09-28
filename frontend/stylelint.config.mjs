/** @type {import("stylelint").Config} */
const config = {
  extends: ["stylelint-config-standard", "stylelint-config-recess-order"],
  overrides: [
    {
      files: ["*.svelte", "**/*.svelte"],
      customSyntax: "postcss-html",
      rules: {
        "selector-pseudo-class-no-unknown": [
          true,
          { ignorePseudoClasses: ["global"] },
        ],
      },
    },
  ],
};

export default config;
