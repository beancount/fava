/** @type {import("stylelint").Config} */
const config = {
  extends: ["stylelint-config-standard", "stylelint-config-recess-order"],
  overrides: [
    {
      files: ["*.svelte", "**/*.svelte"],
      customSyntax: "postcss-html",
      rules: {
        // false positives in stylelint 16.23.1:
        "no-invalid-position-declaration": null,
        "selector-pseudo-class-no-unknown": [
          true,
          { ignorePseudoClasses: ["global"] },
        ],
      },
    },
  ],
};

export default config;
