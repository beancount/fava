/** @type {import("stylelint").Config} */
const config = {
  extends: ["stylelint-config-standard"],
  overrides: [
    {
      files: ["*.svelte", "**/*.svelte"],
      customSyntax: "postcss-html",
      rules: {
        // false positives in stylelint 17.14.1:
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
