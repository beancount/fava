import { readFileSync } from "node:fs";
import { registerHooks } from "node:module";
import { fileURLToPath } from "node:url";

import { compile } from "svelte/compiler";

registerHooks({
  load(url, context, nextLoad) {
    if (url.endsWith(".svelte")) {
      const filename = fileURLToPath(url);
      const raw_source = readFileSync(filename, "utf8");
      const result = compile(raw_source, { filename });
      const source = `${result.js.code}\n//# sourceMappingURL=${result.js.map.toUrl()}`;
      return { format: "module", source, shortCircuit: true };
    }

    return nextLoad(url, context);
  },
});
