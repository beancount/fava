const config = {
  extends: ["stylelint-config-standard", "stylelint-config-recess-order"],
  customSyntax: "postcss-html",
  rules: {
    "selector-pseudo-class-no-unknown": [
      true,
      { ignorePseudoClasses: ["global"] },
    ],
    // The following rule leads to a Svelte parsing error currently.
    // Should be fixed in the next Svelte release after 3.58.0
    "media-feature-range-notation": null,
  },
};

module.exports = config;
