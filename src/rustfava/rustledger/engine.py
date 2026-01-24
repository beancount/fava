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


# Supported API version prefix
SUPPORTED_API_VERSION = "1."


class RustledgerError(Exception):
    """Error from rustledger execution."""


class RustledgerAPIVersionError(RustledgerError):
    """Incompatible API version from rustledger."""


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
        *,
        allow_dir: str | None = None,
    ) -> str:
        """Run rustledger-wasi with given arguments.

        Args:
            args: Command arguments (e.g., ["load"], ["query", "SELECT ..."])
            stdin_data: Data to pass via stdin
            allow_dir: Directory to allow WASM access to (for file operations)

        Returns:
            stdout output as string

        Raises:
            RustledgerError: If the command fails

        Exit codes:
            0 = Success (stdout has valid JSON)
            1 = User error (stderr has error message, not JSON)
            2 = Internal error (serialization failures)
        """
        cmd = [
            self._wasmtime,
            "run",
        ]
        if allow_dir:
            cmd.extend(["--dir", allow_dir])
        cmd.extend([
            str(self._wasm_path),
            *args,
        ])

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

        # Handle exit codes per rustledger FFI spec
        if result.returncode == 1:
            # User error - stderr has the error message (not JSON)
            error_msg = result.stderr.strip() or "Unknown user error"
            raise RustledgerError(error_msg)
        if result.returncode == 2:
            # Internal error
            error_msg = result.stderr.strip() or "Internal rustledger error"
            raise RustledgerError(f"Internal error: {error_msg}")
        if result.returncode != 0:
            # Other non-zero exit code
            error_msg = result.stderr.strip() or f"Exit code {result.returncode}"
            raise RustledgerError(error_msg)

        return result.stdout

    def _parse_response(self, json_str: str) -> dict[str, Any]:
        """Parse JSON response and check API version.

        Args:
            json_str: JSON string from rustledger

        Returns:
            Parsed JSON dict

        Raises:
            RustledgerAPIVersionError: If API version is incompatible
        """
        data = json.loads(json_str)
        api_version = data.get("api_version")

        # Accept responses without api_version (legacy/pre-1.0 format)
        # Once rustledger 1.0 is deployed, we can make this stricter
        if api_version is not None and not api_version.startswith(
            SUPPORTED_API_VERSION
        ):
            msg = (
                f"Incompatible rustledger API version: {api_version}. "
                f"Expected {SUPPORTED_API_VERSION}x"
            )
            raise RustledgerAPIVersionError(msg)
        return data

    def load(self, source: str, filename: str = "<stdin>") -> dict[str, Any]:
        """Load/parse beancount source and return entries, errors, options.

        Args:
            source: Beancount source code
            filename: Filename to use in metadata (for error reporting)

        Returns:
            Dict with keys: api_version, entries, errors, options
        """
        # Pass filename as argument if provided
        args = ["load"]
        if filename != "<stdin>":
            args.append(filename)

        result_json = self._run(args, stdin_data=source)
        return self._parse_response(result_json)

    def query(self, source: str, query_string: str) -> dict[str, Any]:
        """Run a BQL query against beancount source.

        Args:
            source: Beancount source code
            query_string: BQL query

        Returns:
            Dict with keys: api_version, columns, rows, errors
        """
        result_json = self._run(["query", query_string], stdin_data=source)
        return self._parse_response(result_json)

    def validate(self, source: str) -> dict[str, Any]:
        """Validate beancount source.

        Args:
            source: Beancount source code

        Returns:
            Dict with keys: api_version, valid, errors
        """
        result_json = self._run(["validate"], stdin_data=source)
        return self._parse_response(result_json)

    def version(self) -> str:
        """Get rustledger version string."""
        result_json = self._run(["version"])
        data = self._parse_response(result_json)
        return data.get("version", "unknown")

    def format_entries(self, source: str) -> str:
        """Format beancount source to canonical form.

        Args:
            source: Beancount source code

        Returns:
            Formatted beancount source
        """
        result_json = self._run(["format"], stdin_data=source)
        data = self._parse_response(result_json)
        return data.get("formatted", "")

    def is_encrypted(self, filepath: str) -> bool:
        """Check if a file is GPG encrypted.

        Args:
            filepath: Path to file

        Returns:
            True if file is encrypted
        """
        # Resolve to absolute path for WASM file access
        file_path = Path(filepath).resolve()
        allow_dir = str(file_path.parent)
        result_json = self._run(
            ["is-encrypted", str(file_path)],
            allow_dir=allow_dir,
        )
        data = self._parse_response(result_json)
        return data.get("encrypted", False)

    def get_account_type(self, account: str) -> str:
        """Get the type of an account (Assets, Liabilities, etc).

        Args:
            account: Account name

        Returns:
            Account type string
        """
        result_json = self._run(["get-account-type", account])
        data = self._parse_response(result_json)
        return data.get("account_type", "")

    def clamp(
        self,
        source: str,
        begin_date: str,
        end_date: str,
    ) -> dict[str, Any]:
        """Filter entries to date range with opening balances.

        Args:
            source: Beancount source code
            begin_date: Start date (ISO format)
            end_date: End date (ISO format)

        Returns:
            Dict with keys: api_version, entries, errors
        """
        result_json = self._run(
            ["clamp", begin_date, end_date],
            stdin_data=source,
        )
        return self._parse_response(result_json)

    def clamp_entries(
        self,
        entries_json: list[dict[str, Any]],
        begin_date: str,
        end_date: str,
    ) -> dict[str, Any]:
        """Filter entries to date range with opening balances.

        Unlike clamp(), this operates on already-parsed entries JSON,
        avoiding the need to re-parse source code.

        Args:
            entries_json: List of entry dicts (same format as load output)
            begin_date: Start date (ISO format)
            end_date: End date (ISO format)

        Returns:
            Dict with keys: api_version, entries, errors
        """
        input_data = json.dumps({
            "entries": entries_json,
            "begin_date": begin_date,
            "end_date": end_date,
        })
        result_json = self._run(
            ["clamp-entries"],
            stdin_data=input_data,
        )
        return self._parse_response(result_json)

    def types(self) -> dict[str, Any]:
        """Get type constants (MISSING, Booking, ALL_DIRECTIVES).

        Returns:
            Dict with keys: api_version, all_directives, booking_methods, ...
        """
        result_json = self._run(["types"])
        return self._parse_response(result_json)

    def format_entry(self, entry_json: dict[str, Any]) -> str:
        """Format a single entry to beancount string.

        Args:
            entry_json: Entry as JSON dict (same format as load output)

        Returns:
            Formatted beancount string
        """
        result_json = self._run(
            ["format-entry"],
            stdin_data=json.dumps(entry_json),
        )
        data = self._parse_response(result_json)
        return data.get("formatted", "")

    def format_entries_json(self, entries_json: list[dict[str, Any]]) -> str:
        """Format multiple entries to beancount string.

        Args:
            entries_json: List of entries as JSON dicts

        Returns:
            Formatted beancount string (concatenated)
        """
        result_json = self._run(
            ["format-entries"],
            stdin_data=json.dumps(entries_json),
        )
        data = self._parse_response(result_json)
        return data.get("formatted", "")

    def create_entry(self, entry_json: dict[str, Any]) -> dict[str, Any]:
        """Create an entry with hash from JSON.

        Args:
            entry_json: Entry specification (type, date, postings, etc.)

        Returns:
            Complete entry dict with meta and hash
        """
        result_json = self._run(
            ["create-entry"],
            stdin_data=json.dumps(entry_json),
        )
        data = self._parse_response(result_json)
        return data.get("entry", {})

    def create_entries(
        self, entries_json: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Create multiple entries with hashes from JSON.

        Args:
            entries_json: List of entry specifications

        Returns:
            List of complete entry dicts with meta and hashes
        """
        result_json = self._run(
            ["create-entries"],
            stdin_data=json.dumps(entries_json),
        )
        data = self._parse_response(result_json)
        return data.get("entries", [])

    def load_full(
        self,
        filepath: str,
        plugins: list[str] | None = None,
    ) -> dict[str, Any]:
        """Load a beancount file with full processing.

        This uses rustledger-loader for:
        - Include resolution with cycle detection
        - Path security (prevents path traversal)
        - GPG decryption for encrypted files
        - Native plugin execution

        Args:
            filepath: Path to the main beancount file
            plugins: Optional list of plugin names to run (e.g., ["auto_accounts"])

        Returns:
            Dict with keys:
                - api_version: API version string
                - entries: List of directive dicts (sorted, with hashes)
                - errors: List of error dicts
                - options: Options dict
                - plugins: List of plugin directives from file
                - loaded_files: List of all resolved include files
        """
        file_path = Path(filepath).resolve()
        allow_dir = str(file_path.parent)

        # Build command args
        args = ["load-full", str(file_path)]
        if plugins:
            args.extend(plugins)

        result_json = self._run(args, allow_dir=allow_dir)
        return self._parse_response(result_json)

    def filter_entries(
        self,
        entries_json: list[dict[str, Any]],
        begin_date: str,
        end_date: str,
    ) -> dict[str, Any]:
        """Filter entries by date range.

        This filters already-parsed entries without re-parsing source.
        Useful for Fava's date navigation.

        Filtering rules (matching beancount behavior):
        - Open: Include if date < end_date (still active)
        - Close: Include if date >= begin_date
        - Commodity: Always exclude
        - All others: Include if begin_date <= date < end_date

        Args:
            entries_json: List of entry dicts (same format as load output)
            begin_date: Start date (ISO format, inclusive)
            end_date: End date (ISO format, exclusive)

        Returns:
            Dict with keys: api_version, entries, errors
        """
        input_data = {
            "entries": entries_json,
            "begin_date": begin_date,
            "end_date": end_date,
        }
        result_json = self._run(
            ["filter-entries"],
            stdin_data=json.dumps(input_data),
        )
        return self._parse_response(result_json)
