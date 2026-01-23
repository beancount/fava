"""Rustledger WASM engine using wasmtime CLI.

This module provides a Python interface to rustledger-wasi via the wasmtime
CLI. The WASM module uses stdin/stdout for I/O with JSON serialization.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class RustledgerError(Exception):
    """Error from rustledger execution."""


class RustledgerEngine:
    """Interface to rustledger WASM module via wasmtime CLI.

    The rustledger-wasi module is a CLI that reads from stdin and writes
    JSON to stdout. Commands:
    - load [filename]: Parse source → entries + errors + options
    - query <bql>: Execute BQL → columns + rows + errors
    - validate: Parse + validate → valid + errors
    - version: → version string
    """

    _instance: RustledgerEngine | None = None

    def __init__(self, wasm_path: Path | None = None) -> None:
        """Initialize the rustledger engine.

        Args:
            wasm_path: Path to rustledger-wasi.wasm. If None, uses bundled WASM.
        """
        if wasm_path is None:
            wasm_path = Path(__file__).parent / "rustledger-wasi.wasm"

        if not wasm_path.exists():
            msg = f"Rustledger WASM not found at {wasm_path}"
            raise FileNotFoundError(msg)

        self._wasm_path = wasm_path

        # Find wasmtime binary
        self._wasmtime = shutil.which("wasmtime")
        if self._wasmtime is None:
            msg = "wasmtime not found in PATH. Install with: cargo install wasmtime-cli"
            raise RuntimeError(msg)

    @classmethod
    def get_instance(cls, wasm_path: Path | None = None) -> RustledgerEngine:
        """Get singleton engine instance."""
        if cls._instance is None:
            cls._instance = cls(wasm_path)
        return cls._instance

    def _run(
        self,
        args: list[str],
        stdin_data: str | None = None,
    ) -> str:
        """Run rustledger-wasi with given arguments.

        Args:
            args: Command arguments (e.g., ["load"], ["query", "SELECT ..."])
            stdin_data: Data to pass via stdin

        Returns:
            stdout output as string

        Raises:
            RustledgerError: If the command fails
        """
        cmd = [
            self._wasmtime,
            "run",
            str(self._wasm_path),
            *args,
        ]

        try:
            result = subprocess.run(
                cmd,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                check=False,
            )
        except subprocess.TimeoutExpired as e:
            msg = f"Rustledger timed out: {e}"
            raise RustledgerError(msg) from e
        except OSError as e:
            msg = f"Failed to run wasmtime: {e}"
            raise RustledgerError(msg) from e

        if result.returncode != 0:
            error_msg = result.stderr.strip() or f"Exit code {result.returncode}"
            msg = f"Rustledger error: {error_msg}"
            raise RustledgerError(msg)

        return result.stdout

    def load(self, source: str, filename: str = "<stdin>") -> dict[str, Any]:
        """Load/parse beancount source and return entries, errors, options.

        Args:
            source: Beancount source code
            filename: Filename to use in metadata (for error reporting)

        Returns:
            Dict with keys: entries, errors, options
        """
        # Pass filename as argument if provided
        args = ["load"]
        if filename != "<stdin>":
            args.append(filename)

        result_json = self._run(args, stdin_data=source)
        return json.loads(result_json)

    def query(self, source: str, query_string: str) -> dict[str, Any]:
        """Run a BQL query against beancount source.

        Args:
            source: Beancount source code
            query_string: BQL query

        Returns:
            Dict with keys: columns, rows, errors
        """
        result_json = self._run(["query", query_string], stdin_data=source)
        return json.loads(result_json)

    def validate(self, source: str) -> dict[str, Any]:
        """Validate beancount source.

        Args:
            source: Beancount source code

        Returns:
            Dict with keys: valid, errors
        """
        result_json = self._run(["validate"], stdin_data=source)
        return json.loads(result_json)

    def version(self) -> str:
        """Get rustledger version string."""
        result_json = self._run(["version"])
        data = json.loads(result_json)
        return data.get("version", "unknown")
