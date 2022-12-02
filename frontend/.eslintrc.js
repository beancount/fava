const OFF = 0;

const airbnbConfigOverrides = {
  "max-classes-per-file": OFF,
  "no-param-reassign": ["error", { props: false }],
  "no-restricted-syntax": [
    "error",
    "ForInStatement",
    "LabelStatement",
    "WithStatement",
  ],
  "no-underscore-dangle": OFF,
  "import/extensions": OFF,
  "import/no-unresolved": OFF,
  "import/prefer-default-export": OFF,
  "@typescript-eslint/naming-convention": OFF,
};

// Sort import statements and members alphabetically.
const sortImports = {
  "sort-imports": ["warn", { ignoreDeclarationSort: true, ignoreCase: true }],
  "import/order": [
    "warn",
    {
      "newlines-between": "always",
      alphabetize: { order: "asc", caseInsensitive: true },
    },
  ],
};

module.exports = {
  plugins: ["@typescript-eslint", "svelte"],
  extends: [
    "airbnb-base",
    "airbnb-typescript/base",
    "plugin:svelte/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "plugin:@typescript-eslint/strict",
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
    "@typescript-eslint/consistent-type-imports": "warn",
    curly: ["error", "all"],
  },
  overrides: [
    {
      files: "*.svelte",
      parser: "svelte-eslint-parser",
      parserOptions: {
        parser: "@typescript-eslint/parser",
      },
      rules: {
        "svelte/button-has-type": 1,
        "svelte/valid-compile": OFF,
        // this seems to have a few false positives
        "svelte/no-unused-svelte-ignore": OFF,
        "no-self-assign": OFF,
        "no-undef-init": OFF,
        "import/first": OFF,
        "import/no-mutable-exports": OFF,
        "@typescript-eslint/no-unsafe-argument": OFF,
        "@typescript-eslint/no-unsafe-assignment": OFF,
        "@typescript-eslint/no-unsafe-call": OFF,
        "@typescript-eslint/no-unsafe-member-access": OFF,
        "@typescript-eslint/no-misused-promises": OFF,
        // Has some false positives in Svelte files were we have if()
        // checks to trigger re-computations:
        "@typescript-eslint/no-unnecessary-condition": OFF,
      },
    },
  ],
};
