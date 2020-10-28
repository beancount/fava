import { copyFile as fsCopyFile, mkdir as fsMkdir } from "fs";
import { promisify } from "util";
import { basename, dirname, join } from "path";

const copyFile = promisify(fsCopyFile);
const mkdir = promisify(fsMkdir);

/**
 * Copy the fonts over to the bundle folder.
 */
export default function copy(files) {
  return {
    name: "rollup-plugin-copy",
    async generateBundle(options) {
      const outdir = options.file ? dirname(options.file) : options.dir;
      await mkdir(outdir, { recursive: true });
      return Promise.all(
        files.map((file) => copyFile(file, join(outdir, basename(file))))
      );
    },
  };
}
