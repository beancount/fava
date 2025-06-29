import { readFileSync } from "node:fs";
import { registerHooks } from "node:module";
import { fileURLToPath } from "node:url";

import { transformSync } from "esbuild";
import { compile } from "svelte/compiler";

registerHooks({
  load(url, context, nextLoad) {
    if (url.endsWith(".ts")) {
      const filename = fileURLToPath(url);
      const raw_source = readFileSync(filename, "utf8");
      const result = transformSync(raw_source, {
        loader: "ts",
        sourcefile: filename,
        sourcemap: "inline",
      });
      const source = result.code;
      return { format: "module", source, shortCircuit: true };
    } else if (url.endsWith(".svelte")) {
      const filename = fileURLToPath(url);
      const raw_source = readFileSync(filename, "utf8");
      const result = compile(raw_source, { filename });
      const source = `${result.js.code}\n//# sourceMappingURL=${result.js.map.toUrl()}`;
      return { format: "module", source, shortCircuit: true };
    }

    return nextLoad(url, context);
  },
  resolve(specifier, context, nextResolve) {
    if (specifier.startsWith(".") && !specifier.endsWith(".ts")) {
      try {
        // Resolve dir imports that are not supported by ES imports
        return nextResolve(`${specifier}/index.ts`, context);
      } catch {
        try {
          // Try adding .ts extension
          return nextResolve(`${specifier}.ts`, context);
        } catch {
          // Fall back to original resolution
        }
      }
    }

    return nextResolve(specifier, context);
  },
});
