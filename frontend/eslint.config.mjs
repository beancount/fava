// @ts-check

import eslint from "@eslint/js";
import simpleImportSort from "eslint-plugin-simple-import-sort";
import eslintPluginSvelte from "eslint-plugin-svelte";
import svelteParser from "svelte-eslint-parser";
import tseslint from "typescript-eslint";

const OFF = "off";
const ON = "error";

const tsParserOptions = {
  projectService: true,
  tsconfigRootDir: import.meta.dirname,
  extraFileExtensions: [".svelte"],
};

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  ...eslintPluginSvelte.configs["flat/recommended"],
  {
    languageOptions: {
      parserOptions: tsParserOptions,
    },
    plugins: {
      "simple-import-sort": simpleImportSort,
    },
    rules: {
      "no-undef": OFF, // better handled by Typescript
      "no-param-reassign": ON,
      "no-restricted-syntax": [
        ON,
        "ForInStatement",
        "LabelStatement",
        "WithStatement",
      ],
      "@typescript-eslint/consistent-type-imports": ON,
      "@typescript-eslint/explicit-module-boundary-types": ON,
      "@typescript-eslint/promise-function-async": ON,
      "@typescript-eslint/strict-boolean-expressions": ON,
      curly: [ON, "all"],
      eqeqeq: [ON, "smart"],
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
      // Sort import statements and members alphabetically.
      "simple-import-sort/imports": ON,
      "simple-import-sort/exports": ON,
    },
  },
  {
    files: ["**/*.svelte"],
    languageOptions: {
      parser: svelteParser,
      parserOptions: {
        ...tsParserOptions,
        parser: tseslint.parser,
      },
    },
    rules: {
      "svelte/button-has-type": ON,
    },
  },
);
