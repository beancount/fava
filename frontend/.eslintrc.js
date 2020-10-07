const airbnbConfigOverrides = {
  "max-classes-per-file": 0,
  "no-param-reassign": ["error", { props: false }],
  "no-restricted-syntax": [
    "error",
    "ForInStatement",
    "LabelStatement",
    "WithStatement",
  ],
  "import/extensions": 0,
  "import/no-unresolved": 0,
  "import/prefer-default-export": 0,
  "@typescript-eslint/naming-convention": 0,
};

module.exports = {
  plugins: ["@typescript-eslint", "svelte3"],
  extends: [
    "airbnb-typescript/base",
    "plugin:@typescript-eslint/recommended",
    // "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "prettier",
    "prettier/@typescript-eslint",
  ],
  parserOptions: {
    tsconfigRootDir: __dirname,
    project: ["./tsconfig.json"],
  },
  rules: {
    ...airbnbConfigOverrides,
    curly: ["error", "all"],
  },
  overrides: [
    {
      files: "*.js",
      rules: {
        "@typescript-eslint/explicit-function-return-type": 0,
      },
    },
    {
      files: "*.svelte",
      processor: "svelte3/svelte3",
      rules: {
        "no-undef-init": 0,
        "import/first": 0,
        "import/no-mutable-exports": 0,
        "@typescript-eslint/explicit-function-return-type": 0,
      },
    },
    {
      files: "*.ts",
      parser: "@typescript-eslint/parser",
    },
  ],
};
