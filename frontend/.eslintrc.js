const airbnbConfigOverrides = {
  "max-classes-per-file": 0,
  "no-param-reassign": ["error", { props: false }],
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
  "@typescript-eslint/naming-convention": 0,
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
  plugins: ["@typescript-eslint", "svelte3"],
  extends: [
    "airbnb-typescript/base",
    "plugin:@typescript-eslint/recommended",
    "prettier",
    "prettier/@typescript-eslint",
  ],
  env: { browser: true },
  parserOptions: {
    tsconfigRootDir: __dirname,
    project: ["./tsconfig.json", "./tsconfig.confs.json"],
    extraFileExtensions: [".svelte"],
  },
  rules: {
    ...airbnbConfigOverrides,
    curly: ["error", "all"],
  },
  overrides: [
    {
      files: "*.js",
      rules: {
        "@typescript-eslint/explicit-module-boundary-types": 0,
      },
    },
    {
      files: "*.svelte",
      processor: "svelte3/svelte3",
      rules: {
        "no-undef-init": 0,
        "import/first": 0,
        "import/no-mutable-exports": 0,
      },
    },
    {
      files: "*.ts",
      parser: "@typescript-eslint/parser",
      extends: [
        "plugin:@typescript-eslint/recommended-requiring-type-checking",
      ],
      rules: {
        ...sortImports,
      },
    },
  ],
};
