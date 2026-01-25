#!/usr/bin/env bun
/**
 * Ensures rustledger binaries are built before running the desktop app.
 * Uses caching to avoid unnecessary rebuilds.
 *
 * By default, uses the latest v* tagged release.
 * Use --main to build from the main branch instead.
 */

import { execSync, spawnSync } from "child_process";
import { existsSync, readFileSync, mkdirSync, writeFileSync, cpSync } from "fs";
import { join, dirname } from "path";

const ROOT_DIR = join(dirname(import.meta.dir), "..");
const CACHE_DIR = join(ROOT_DIR, ".cache", "rustledger");
const BINARIES_DIR = join(dirname(import.meta.dir), "src-tauri", "binaries");
const WASM_PATH = join(ROOT_DIR, "src", "rustfava", "rustledger", "rustledger-wasi.wasm");
const WASM_VERSION_PATH = join(ROOT_DIR, "src", "rustfava", "rustledger", ".wasm-version");
const RUSTLEDGER_REPO = "https://github.com/rustledger/rustledger.git";

// CLI binaries to build
const CLI_BINARIES = [
  "bean-check", "bean-doctor", "bean-extract", "bean-format",
  "bean-price", "bean-query", "bean-report",
  "rledger"
];

function getTargetTriple(): string {
  try {
    const output = execSync("rustc -vV", { encoding: "utf-8" });
    const match = output.match(/host: (.+)/);
    return match ? match[1].trim() : "unknown";
  } catch {
    console.error("Failed to get target triple. Is Rust installed?");
    process.exit(1);
  }
}

function getGitRef(dir: string): string | null {
  try {
    // Try to get tag first, fall back to commit
    const tag = execSync("git describe --tags --exact-match 2>/dev/null || true", {
      cwd: dir,
      encoding: "utf-8"
    }).trim();
    if (tag) return tag;
    return execSync("git rev-parse HEAD", { cwd: dir, encoding: "utf-8" }).trim();
  } catch {
    return null;
  }
}

function getLatestTag(): string {
  try {
    // Get latest v* tag from remote
    const output = execSync(
      `git ls-remote --tags --sort=-v:refname ${RUSTLEDGER_REPO} "v*" | head -1`,
      { encoding: "utf-8" }
    );
    const match = output.match(/refs\/tags\/(v[^\s^]+)/);
    if (match) return match[1];
    throw new Error("No tags found");
  } catch (err) {
    console.error("Failed to get latest tag, falling back to main");
    return "main";
  }
}

function cloneRepo(ref: string): string {
  console.log(`Cloning rustledger repository (${ref})...`);
  mkdirSync(dirname(CACHE_DIR), { recursive: true });

  if (ref === "main") {
    execSync(`git clone --depth 1 -b main ${RUSTLEDGER_REPO} ${CACHE_DIR}`, { stdio: "inherit" });
  } else {
    // For tags, clone then checkout the tag
    execSync(`git clone --depth 1 --branch ${ref} ${RUSTLEDGER_REPO} ${CACHE_DIR}`, { stdio: "inherit" });
  }
  return getGitRef(CACHE_DIR) || "unknown";
}

function getCurrentRef(): string | null {
  if (!existsSync(CACHE_DIR)) return null;
  return getGitRef(CACHE_DIR);
}

function switchToRef(ref: string): string {
  console.log(`Switching to ${ref}...`);

  // Fetch the ref
  if (ref === "main") {
    execSync("git fetch --depth 1 origin main", { cwd: CACHE_DIR, stdio: "inherit" });
    execSync("git checkout main", { cwd: CACHE_DIR, stdio: "inherit" });
    execSync("git reset --hard origin/main", { cwd: CACHE_DIR, stdio: "inherit" });
  } else {
    execSync(`git fetch --depth 1 origin tag ${ref}`, { cwd: CACHE_DIR, stdio: "inherit" });
    execSync(`git checkout ${ref}`, { cwd: CACHE_DIR, stdio: "inherit" });
  }

  return getGitRef(CACHE_DIR) || "unknown";
}

function ensureRepo(useMain: boolean, forceUpdate: boolean): string {
  const targetRef = useMain ? "main" : getLatestTag();
  console.log(`Target: ${targetRef}${useMain ? " (main branch)" : " (latest release)"}`);

  if (!existsSync(CACHE_DIR)) {
    return cloneRepo(targetRef);
  }

  const currentRef = getCurrentRef();
  console.log(`Currently at: ${currentRef}`);

  // If forcing update or ref changed, switch
  if (forceUpdate || currentRef !== targetRef) {
    return switchToRef(targetRef);
  }

  return currentRef || "unknown";
}

function readVersionFile(path: string): string | null {
  try {
    return readFileSync(path, "utf-8").trim();
  } catch {
    return null;
  }
}

function needsWasmBuild(currentCommit: string): boolean {
  if (!existsSync(WASM_PATH)) {
    console.log("WASM file missing, needs build");
    return true;
  }
  const builtCommit = readVersionFile(WASM_VERSION_PATH);
  if (builtCommit !== currentCommit) {
    console.log(`WASM outdated (built: ${builtCommit?.slice(0, 8)}, current: ${currentCommit.slice(0, 8)})`);
    return true;
  }
  return false;
}

function needsCliBuild(currentCommit: string, targetTriple: string): boolean {
  const versionFile = join(BINARIES_DIR, `.cli-version-${targetTriple}`);

  // Check if any binary is missing
  for (const bin of CLI_BINARIES) {
    const binPath = join(BINARIES_DIR, `${bin}-${targetTriple}`);
    if (!existsSync(binPath)) {
      console.log(`CLI binary missing: ${bin}, needs build`);
      return true;
    }
  }

  const builtCommit = readVersionFile(versionFile);
  if (builtCommit !== currentCommit) {
    console.log(`CLI outdated (built: ${builtCommit?.slice(0, 8)}, current: ${currentCommit.slice(0, 8)})`);
    return true;
  }
  return false;
}

function buildWasm(currentCommit: string): void {
  console.log("Building rustledger WASM module...");

  // Try to add wasm target via rustup (may not be available in nix)
  spawnSync("rustup", ["target", "add", "wasm32-wasip1"], { stdio: "pipe" });

  // Build the FFI WASI crate specifically
  const result = spawnSync("cargo", [
    "build",
    "--target", "wasm32-wasip1",
    "--release",
    "-p", "rustledger-ffi-wasi"
  ], {
    cwd: CACHE_DIR,
    stdio: "inherit"
  });

  if (result.status !== 0) {
    console.error("Failed to build WASM");
    process.exit(1);
  }

  // Copy WASM file (binary name matches crate name)
  const wasmSource = join(CACHE_DIR, "target", "wasm32-wasip1", "release", "rustledger-ffi-wasi.wasm");
  cpSync(wasmSource, WASM_PATH);
  writeFileSync(WASM_VERSION_PATH, currentCommit);
  console.log(`WASM built successfully (commit: ${currentCommit.slice(0, 8)})`);
}

function buildCli(currentCommit: string, targetTriple: string): void {
  console.log("Building rustledger CLI binaries...");

  // Build
  const result = spawnSync("cargo", ["build", "--release"], {
    cwd: CACHE_DIR,
    stdio: "inherit"
  });

  if (result.status !== 0) {
    console.error("Failed to build CLI binaries");
    process.exit(1);
  }

  // Copy binaries
  mkdirSync(BINARIES_DIR, { recursive: true });
  for (const bin of CLI_BINARIES) {
    const source = join(CACHE_DIR, "target", "release", bin);
    const dest = join(BINARIES_DIR, `${bin}-${targetTriple}`);
    if (existsSync(source)) {
      cpSync(source, dest);
    }
  }

  // Write version file
  const versionFile = join(BINARIES_DIR, `.cli-version-${targetTriple}`);
  writeFileSync(versionFile, currentCommit);
  console.log(`CLI binaries built successfully (commit: ${currentCommit.slice(0, 8)})`);
}

async function main() {
  const args = process.argv.slice(2);
  const useMain = args.includes("--main");
  const forceUpdate = args.includes("--update");
  const forceRebuild = args.includes("--force");

  console.log("Ensuring rustledger is built...");
  if (useMain) {
    console.log("(using main branch for bleeding-edge development)\n");
  } else {
    console.log("(using latest tagged release)\n");
  }

  const targetTriple = getTargetTriple();
  console.log(`Build target: ${targetTriple}`);

  // Ensure repo is at the correct ref
  const currentRef = ensureRepo(useMain, forceUpdate);
  console.log(`Rustledger: ${currentRef}\n`);

  // Check and build WASM
  if (forceRebuild || needsWasmBuild(currentRef)) {
    buildWasm(currentRef);
  } else {
    console.log("WASM is up to date");
  }

  // Check and build CLI
  if (forceRebuild || needsCliBuild(currentRef, targetTriple)) {
    buildCli(currentRef, targetTriple);
  } else {
    console.log("CLI binaries are up to date");
  }

  console.log("\nRustledger ready!");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
