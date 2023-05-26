declare module "*.wasm" {
  /** Relative path to the output filename (since we use the esbuild `file` loader). */
  const filename: string;
  export default filename;
}
