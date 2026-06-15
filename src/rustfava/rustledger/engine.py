"""Rustledger WASM engine using wasmtime CLI with JSON-RPC 2.0.

This module provides a Python interface to rustledger-wasi via the wasmtime
CLI. The WASM module uses JSON-RPC 2.0 protocol over stdin/stdout.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


# Supported API version prefix
SUPPORTED_API_VERSION = "1."

# Rustledger release to download
RUSTLEDGER_VERSION = "v0.16.0"
RUSTLEDGER_WASM_URL = (
    f"https://github.com/rustledger/rustledger/releases/download/"
    f"{RUSTLEDGER_VERSION}/rustledger-ffi-wasi-{RUSTLEDGER_VERSION}.wasm"
)


class RustledgerError(Exception):
    """Error from rustledger execution."""


class RustledgerAPIVersionError(RustledgerError):
    """Incompatible API version from rustledger."""


class RustledgerEngine:
    """Interface to rustledger WASM module via wasmtime CLI.

    The rustledger-wasi module uses JSON-RPC 2.0 protocol:
    - Request: {"jsonrpc": "2.0", "method": "...", "params": {...}, "id": 1}
    - Response: {"jsonrpc": "2.0", "result": {...}, "id": 1}
    - Error: {"jsonrpc": "2.0", "error": {"code": ..., "message": "..."}, "id": 1}

    Methods:
    - ledger.load: Parse source → entries + errors + options
    - ledger.loadFile: Load file with includes → entries + errors + options
    - query.execute: Execute BQL → columns + rows + errors
    - ledger.validate: Validate source → valid + errors
    - util.version: → apiVersion + version
    """

    _instance: RustledgerEngine | None = None
    _request_id: int = 0

    def __init__(self, wasm_path: Path | None = None) -> None:
        """Initialize the rustledger engine.

        Args:
            wasm_path: Path to rustledger-wasi.wasm. If None, uses default path.
        """
        if wasm_path is None:
            wasm_path = Path(__file__).parent / "rustledger-wasi.wasm"

        if not wasm_path.exists():
            self._download_wasm(wasm_path)

        self._wasm_path = wasm_path

        # Find wasmtime binary
        self._wasmtime = shutil.which("wasmtime")
        if self._wasmtime is None:
            msg = "wasmtime not found in PATH. Install with: cargo install wasmtime-cli"
            raise RuntimeError(msg)

    @staticmethod
    def _download_wasm(wasm_path: Path) -> None:
        """Download the rustledger WASM module."""
        import sys

        print(  # noqa: T201
            f"Downloading rustledger WASM ({RUSTLEDGER_VERSION})...",
            file=sys.stderr,
        )
        try:
            wasm_path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(RUSTLEDGER_WASM_URL, wasm_path)  # noqa: S310
            print("Done.", file=sys.stderr)  # noqa: T201
        except Exception as e:
            msg = f"Failed to download rustledger WASM: {e}"
            raise RuntimeError(msg) from e

    @classmethod
    def get_instance(cls, wasm_path: Path | None = None) -> RustledgerEngine:
        """Get singleton engine instance."""
        if cls._instance is None:
            cls._instance = cls(wasm_path)
        return cls._instance

    def _next_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id

    def _rpc_call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        allow_dir: str | None = None,
    ) -> dict[str, Any]:
        """Make a JSON-RPC 2.0 call to rustledger-wasi.

        Args:
            method: JSON-RPC method name (e.g., "ledger.load", "query.execute")
            params: Method parameters
            allow_dir: Directory to allow WASM access to (for file operations)

        Returns:
            Result dict from the JSON-RPC response

        Raises:
            RustledgerError: If the call fails
        """
        # Build JSON-RPC request
        request: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._next_id(),
        }
        if params:
            request["params"] = params

        request_json = json.dumps(request)

        # Build wasmtime command
        assert self._wasmtime is not None
        cmd: list[str] = [self._wasmtime, "run"]
        if allow_dir:
            cmd.extend(["--dir", allow_dir])
        cmd.append(str(self._wasm_path))

        try:
            result = subprocess.run(
                cmd,
                input=request_json,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except subprocess.TimeoutExpired as e:
            msg = f"Rustledger timed out: {e}"
            raise RustledgerError(msg) from e
        except OSError as e:
            msg = f"Failed to run wasmtime: {e}"
            raise RustledgerError(msg) from e

        # JSON-RPC always returns valid JSON on stdout (even for errors)
        if not result.stdout.strip():
            error_msg = result.stderr.strip() or f"Exit code {result.returncode}"
            raise RustledgerError(f"Empty response: {error_msg}")

        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise RustledgerError(f"Invalid JSON response: {e}") from e

        # Check for JSON-RPC error
        if "error" in response:
            error = response["error"]
            code = error.get("code", -32603)
            message = error.get("message", "Unknown error")
            raise RustledgerError(f"[{code}] {message}")

        # Return the result
        return dict(response.get("result", {}))

    def load(self, source: str, filename: str = "<stdin>") -> dict[str, Any]:
        """Load/parse beancount source and return entries, errors, options.

        Args:
            source: Beancount source code
            filename: Filename to use in metadata (for error reporting)

        Returns:
            Dict with keys: api_version, entries, errors, options
        """
        params: dict[str, Any] = {"source": source}
        if filename != "<stdin>":
            params["filename"] = filename

        return self._rpc_call("ledger.load", params)

    def query(self, source: str, query_string: str) -> dict[str, Any]:
        """Run a BQL query against beancount source.

        Args:
            source: Beancount source code
            query_string: BQL query

        Returns:
            Dict with keys: api_version, columns, rows, errors
        """
        return self._rpc_call("query.execute", {"source": source, "query": query_string})

    def validate(self, source: str) -> dict[str, Any]:
        """Validate beancount source.

        Args:
            source: Beancount source code

        Returns:
            Dict with keys: api_version, valid, errors
        """
        return self._rpc_call("ledger.validate", {"source": source})

    def version(self) -> str:
        """Get rustledger version string."""
        data = self._rpc_call("util.version")
        return str(data.get("version", "unknown"))

    def format_entries(self, source: str) -> str:
        """Format beancount source to canonical form.

        Args:
            source: Beancount source code

        Returns:
            Formatted beancount source
        """
        data = self._rpc_call("format.source", {"source": source})
        return str(data.get("formatted", ""))

    def is_encrypted(self, filepath: str) -> bool:
        """Check if a file is GPG encrypted.

        Args:
            filepath: Path to file

        Returns:
            True if file is encrypted
        """
        # Resolve to absolute path for WASM file access
        file_path = Path(filepath).resolve()
        # Use root "/" to allow include paths with ".." (parent directory references)
        # This matches native beancount behavior where includes can reference any path
        data = self._rpc_call(
            "util.isEncrypted",
            {"path": str(file_path)},
            allow_dir="/",
        )
        return bool(data.get("encrypted", False))

    def get_account_type(self, account: str) -> str:
        """Get the type of an account (Assets, Liabilities, etc).

        Args:
            account: Account name

        Returns:
            Account type string
        """
        data = self._rpc_call("util.getAccountType", {"account": account})
        return str(data.get("accountType", ""))

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
        # Two-step: load source, then clamp entries
        load_result = self._rpc_call("ledger.load", {"source": source})
        entries = load_result.get("entries", [])

        return self._rpc_call("entry.clamp", {
            "entries": entries,
            "beginDate": begin_date,
            "endDate": end_date,
        })

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
        return self._rpc_call("entry.clamp", {
            "entries": entries_json,
            "beginDate": begin_date,
            "endDate": end_date,
        })

    def types(self) -> dict[str, Any]:
        """Get type constants (MISSING, Booking, ALL_DIRECTIVES).

        Returns:
            Dict with keys: api_version, all_directives, booking_methods, ...
        """
        return self._rpc_call("util.types")

    def format_entry(self, entry_json: dict[str, Any]) -> str:
        """Format a single entry to beancount string.

        Args:
            entry_json: Entry as JSON dict (same format as load output)

        Returns:
            Formatted beancount string
        """
        data = self._rpc_call("format.entry", {"entry": entry_json})
        return str(data.get("formatted", ""))

    def format_entries_json(self, entries_json: list[dict[str, Any]]) -> str:
        """Format multiple entries to beancount string.

        Args:
            entries_json: List of entries as JSON dicts

        Returns:
            Formatted beancount string (concatenated)
        """
        data = self._rpc_call("format.entries", {"entries": entries_json})
        return str(data.get("formatted", ""))

    def create_entry(self, entry_json: dict[str, Any]) -> dict[str, Any]:
        """Create an entry with hash from JSON.

        Args:
            entry_json: Entry specification (type, date, postings, etc.)

        Returns:
            Complete entry dict with meta and hash
        """
        data = self._rpc_call("entry.create", {"entry": entry_json})
        return dict(data.get("entry", {}))

    def create_entries(
        self, entries_json: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Create multiple entries with hashes from JSON.

        Args:
            entries_json: List of entry specifications

        Returns:
            List of complete entry dicts with meta and hashes
        """
        data = self._rpc_call("entry.createBatch", {"entries": entries_json})
        return list(data.get("entries", []))

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
        # Use root "/" to allow include paths with ".." (parent directory references)
        # This matches native beancount behavior where includes can reference any path

        params: dict[str, Any] = {"path": str(file_path)}
        if plugins:
            params["plugins"] = plugins

        return self._rpc_call("ledger.loadFile", params, allow_dir="/")

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
        return self._rpc_call("entry.filter", {
            "entries": entries_json,
            "beginDate": begin_date,
            "endDate": end_date,
        })
