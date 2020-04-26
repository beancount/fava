/* eslint-disable import/no-extraneous-dependencies */

import path from "path";

import { createFilter } from "@rollup/pluginutils";

export default function css(options = {}) {
  const filter = createFilter(options.include || ["**/*.css"], options.exclude);
  const styles = new Map();

  return {
    name: "css",
    transform(code, id) {
      if (!filter(id)) {
        return null;
      }
      styles.set(id, code);
      return {
        code: `export default ${JSON.stringify(code)}`,
        map: { mappings: "" },
      };
    },
    generateBundle(opts) {
      if (styles.size === 0) {
        return;
      }
      const emitOpts = {};
      const file = options.fileName || opts.file;
      if (file) {
        emitOpts.fileName = `${path.basename(file, path.extname(file))}.css`;
      } else {
        emitOpts.name = "styles.css";
      }
      // Emit styles to file
      this.emitFile({
        type: "asset",
        source: [...styles.values()].join(""),
        ...emitOpts,
      });
    },
  };
}
