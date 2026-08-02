import eslint from "@eslint/js";
import { defineConfig } from "eslint/config";
import eslintPluginSvelte from "eslint-plugin-svelte";
import svelteParser from "svelte-eslint-parser";
import tseslint from "typescript-eslint";

const OFF = "off";
const ON = "error";

const tsParserOptions = {
  projectService: true,
  extraFileExtensions: [".svelte"],
};

export default defineConfig(
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  ...eslintPluginSvelte.configs["flat/recommended"],
  {
    languageOptions: {
      parserOptions: tsParserOptions,
    },
    rules: {
      "no-undef": OFF, // better handled by Typescript
      "no-restricted-syntax": [ON, "ForInStatement", "LabelStatement"],
      "@typescript-eslint/no-unused-vars": OFF, // handled by biome, except in svelte files
      "@typescript-eslint/explicit-module-boundary-types": ON,
      "@typescript-eslint/promise-function-async": ON,
      "@typescript-eslint/strict-boolean-expressions": ON,
      "@typescript-eslint/no-floating-promises": [
        ON,
        {
          allowForKnownSafeCalls: [
            { from: "package", name: ["test"], package: "node:test" },
          ],
        },
      ],

      "@typescript-eslint/naming-convention": [
        ON,
        {
          selector: "variable",
          format: ["camelCase", "snake_case", "UPPER_CASE"],
          leadingUnderscore: "allow",
        },
        { selector: "function", format: ["snake_case"] },
        { selector: "typeLike", format: ["PascalCase"] },
      ],
    },
  },
  {
    files: ["**/*.svelte", "**/*.svelte.ts"],
    languageOptions: {
      parser: svelteParser,
      parserOptions: {
        ...tsParserOptions,
        parser: tseslint.parser,
      },
    },
    rules: {
      "@typescript-eslint/no-useless-default-assignment": OFF,
      "@typescript-eslint/no-unused-vars": [ON, { varsIgnorePattern: "^_" }],
    },
  },
);
