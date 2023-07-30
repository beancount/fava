const OFF = 0;
const ON = "error";

const airbnbConfigOverrides = {
  "max-classes-per-file": OFF,
  "class-methods-use-this": OFF,
  "no-param-reassign": [ON, { props: false }],
  "no-restricted-syntax": [
    ON,
    "ForInStatement",
    "LabelStatement",
    "WithStatement",
  ],
  "no-underscore-dangle": OFF,
  "import/prefer-default-export": OFF,
  "@typescript-eslint/naming-convention": [
    ON,
    {
      selector: "variable",
      format: ["camelCase", "PascalCase", "snake_case", "UPPER_CASE"],
    },
    {
      selector: "function",
      format: ["camelCase", "PascalCase", "snake_case"],
    },
    {
      selector: "typeLike",
      format: ["PascalCase"],
    },
  ],
};

// Sort import statements and members alphabetically.
const sortImports = {
  "sort-imports": [ON, { ignoreDeclarationSort: true, ignoreCase: true }],
  "import/order": [
    ON,
    {
      "newlines-between": "always",
      alphabetize: { order: "asc", caseInsensitive: true },
    },
  ],
};

module.exports = {
  extends: [
    "airbnb-base",
    "airbnb-typescript/base",
    "plugin:deprecation/recommended",
    "plugin:svelte/recommended",
    "plugin:@typescript-eslint/recommended-type-checked",
    "plugin:@typescript-eslint/strict-type-checked",
    "plugin:@typescript-eslint/stylistic-type-checked",
    "plugin:svelte/prettier",
    "prettier",
  ],
  env: { browser: true },
  parser: "@typescript-eslint/parser",
  parserOptions: {
    tsconfigRootDir: __dirname,
    project: ["./tsconfig.json", "./tsconfig.confs.json"],
    extraFileExtensions: [".svelte"],
  },
  rules: {
    ...airbnbConfigOverrides,
    ...sortImports,
    "@typescript-eslint/consistent-type-imports": ON,
    "@typescript-eslint/explicit-module-boundary-types": ON,
    curly: [ON, "all"],
  },
  overrides: [
    {
      files: "*.svelte",
      parser: "svelte-eslint-parser",
      parserOptions: {
        parser: "@typescript-eslint/parser",
      },
      rules: {
        "svelte/button-has-type": ON,
        "no-self-assign": OFF,
        "no-undef": OFF,
        "no-undef-init": OFF,
        "import/no-mutable-exports": OFF,
        "@typescript-eslint/no-unsafe-argument": OFF,
        "@typescript-eslint/no-unsafe-assignment": OFF,
        "@typescript-eslint/no-unsafe-call": OFF,
        "@typescript-eslint/no-unsafe-member-access": OFF,
        // Has some false positives in Svelte files were we have if()
        // checks to trigger re-computations:
        "@typescript-eslint/no-unnecessary-condition": OFF,
      },
    },
  ],
};
