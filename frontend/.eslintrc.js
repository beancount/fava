module.exports = {
  plugins: ["@typescript-eslint", "svelte3"],
  extends: [
    "airbnb-typescript/base",
    "plugin:@typescript-eslint/recommended",
    "prettier",
    "prettier/@typescript-eslint",
  ],
  parserOptions: {
    tsconfigRootDir: __dirname,
    project: ["./tsconfig.json"],
  },
  env: {
    browser: true,
  },
  rules: {
    camelcase: 0,
    curly: ["error", "all"],
    "max-classes-per-file": 0,
    "no-param-reassign": 0,
    "no-restricted-syntax": [
      "error",
      "ForInStatement",
      "LabelStatement",
      "WithStatement",
    ],
    "no-underscore-dangle": 0,
    "import/extensions": 0,
    "import/no-unresolved": 0,
    "import/prefer-default-export": 0,
    "@typescript-eslint/camelcase": 0,
    "@typescript-eslint/naming-convention": 0,
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
