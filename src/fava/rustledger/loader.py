"""Loader functions for rustledger - replaces beancount.loader."""

from __future__ import annotations

import importlib
import re
from pathlib import Path
from typing import TYPE_CHECKING

from fava.rustledger.engine import RustledgerEngine
from fava.rustledger.options import options_from_json
from fava.rustledger.types import directives_from_json

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fava.beans.abc import Directive
    from fava.beans.types import BeancountOptions
    from fava.helpers import BeancountError


# Regex to match include directives
INCLUDE_RE = re.compile(r'^include\s+"([^"]+)"', re.MULTILINE)


class SourceMap:
    """Maps byte offsets in concatenated source back to original files."""

    def __init__(self) -> None:
        self.segments: list[tuple[int, int, str, int]] = []
        # (start_offset, end_offset, filename, line_offset)

    def add_segment(
        self, start: int, end: int, filename: str, line_offset: int = 0
    ) -> None:
        """Add a source segment mapping."""
        self.segments.append((start, end, filename, line_offset))

    def resolve(self, offset: int) -> tuple[str, int]:
        """Resolve byte offset to (filename, line_in_file)."""
        for start, end, filename, line_offset in self.segments:
            if start <= offset < end:
                return filename, line_offset
        return "<unknown>", 0


def _resolve_includes(
    main_path: Path,
    *,
    seen: set[Path] | None = None,
) -> tuple[str, list[Path], SourceMap]:
    """Recursively resolve include directives.

    Args:
        main_path: Path to the main beancount file
        seen: Set of already processed files (for cycle detection)

    Returns:
        Tuple of (concatenated source, list of all included file paths, source map)
    """
    if seen is None:
        seen = set()

    source_map = SourceMap()
    main_path = main_path.resolve()

    if main_path in seen:
        # Cycle detected, return empty
        return "", [], source_map

    seen.add(main_path)
    included_files = [main_path]

    try:
        source = main_path.read_text("utf-8")
    except FileNotFoundError:
        # Return error marker that rustledger can handle
        error_source = f';; ERROR: File not found: {main_path}\n'
        return error_source, included_files, source_map
    except UnicodeDecodeError:
        # Try reading with errors='replace' to handle invalid unicode
        source = main_path.read_text("utf-8", errors="replace")

    # Find all include directives
    base_dir = main_path.parent
    parts: list[str] = []
    current_offset = 0
    last_end = 0

    for match in INCLUDE_RE.finditer(source):
        # Add text before the include
        before_include = source[last_end : match.start()]
        if before_include:
            parts.append(before_include)
            # Count lines in this segment for proper line tracking
            current_offset += len(before_include)

        # Resolve the included file
        include_path = (base_dir / match.group(1)).resolve()
        include_source, include_files, _ = _resolve_includes(
            include_path, seen=seen
        )

        if include_source:
            parts.append(include_source)
            current_offset += len(include_source)

        included_files.extend(include_files)
        last_end = match.end()

    # Add remaining text after last include
    remaining = source[last_end:]
    if remaining:
        parts.append(remaining)

    return "".join(parts), included_files, source_map


def _errors_from_json(
    errors_json: list[dict],
    filename: str = "<unknown>",
) -> list[BeancountError]:
    """Convert rustledger errors to Fava BeancountError format."""
    from fava.helpers import BeancountError

    result = []
    for err in errors_json:
        # Handle both old format (source dict) and new format (line field)
        if "source" in err:
            source = err["source"]
            err_filename = source.get("filename", filename)
            err_lineno = source.get("lineno", 0)
        else:
            err_filename = filename
            err_lineno = err.get("line", 0)

        result.append(
            BeancountError(
                source={
                    "filename": err_filename,
                    "lineno": err_lineno,
                },
                message=err.get("message", "Unknown error"),
                entry=None,
            )
        )
    return result


def _auto_accounts(
    entries: list[Directive],
    _options: BeancountOptions,
) -> tuple[list[Directive], list[BeancountError]]:
    """Auto-generate Open directives for accounts used in entries.

    This is a rustledger-compatible implementation of beancount.plugins.auto_accounts.
    """
    from fava.beans.account import get_entry_accounts
    from fava.rustledger.types import RLOpen

    # Find all existing Open entries
    existing_opens: set[str] = set()
    for entry in entries:
        if type(entry).__name__ in ("Open", "RLOpen"):
            existing_opens.add(entry.account)

    # Find all accounts used in entries
    used_accounts: set[str] = set()
    earliest_date = None
    for entry in entries:
        if earliest_date is None or entry.date < earliest_date:
            earliest_date = entry.date
        used_accounts.update(get_entry_accounts(entry))

    # Generate Open entries for accounts that don't have them
    new_opens = []
    for account in sorted(used_accounts - existing_opens):
        new_opens.append(
            RLOpen(
                meta={"filename": "<auto_accounts>", "lineno": 0},
                date=earliest_date,
                account=account,
                currencies=[],
                booking=None,
            )
        )

    return new_opens + list(entries), []


def _run_plugins(
    entries: list[Directive],
    plugins: list[dict],
    options: BeancountOptions,
) -> tuple[list[Directive], list[BeancountError]]:
    """Run Python plugins on entries.

    Args:
        entries: List of parsed entries
        plugins: List of plugin specs from rustledger ({"name": "...", "config": "..."})
        options: Beancount options dict

    Returns:
        Tuple of (processed entries, plugin errors)
    """
    from fava.helpers import BeancountError

    all_errors: list[BeancountError] = []

    for plugin_spec in plugins:
        plugin_name = plugin_spec.get("name", "")
        plugin_config = plugin_spec.get("config")

        if not plugin_name:
            continue

        # Handle beancount.plugins.auto_accounts specially since it doesn't
        # work with rustledger entry types
        if plugin_name == "beancount.plugins.auto_accounts":
            entries, plugin_errors = _auto_accounts(entries, options)
            all_errors.extend(plugin_errors)
            continue

        try:
            module = importlib.import_module(plugin_name)
        except ImportError as e:
            all_errors.append(
                BeancountError(
                    source={"filename": "<plugin>", "lineno": 0},
                    message=f"Failed to import plugin '{plugin_name}': {e}",
                    entry=None,
                )
            )
            continue

        # Get plugin functions from __plugins__ attribute
        plugin_funcs = getattr(module, "__plugins__", [])
        if not plugin_funcs:
            # Try using the module name as the function name
            func_name = plugin_name.split(".")[-1]
            if hasattr(module, func_name):
                plugin_funcs = [func_name]

        for func_name in plugin_funcs:
            plugin_fn = getattr(module, func_name, None)
            if plugin_fn is None:
                continue

            try:
                # Call plugin: (entries, options) -> (entries, errors)
                # Some plugins use config as second arg instead of options
                if plugin_config is not None:
                    entries, plugin_errors = plugin_fn(entries, plugin_config)
                else:
                    entries, plugin_errors = plugin_fn(entries, options)

                # Convert any plugin errors to our error format
                for err in plugin_errors:
                    if isinstance(err, BeancountError):
                        all_errors.append(err)
                    else:
                        # Handle beancount-style error tuples/namedtuples
                        all_errors.append(
                            BeancountError(
                                source=getattr(err, "source", {"filename": "<plugin>", "lineno": 0}),
                                message=getattr(err, "message", str(err)),
                                entry=getattr(err, "entry", None),
                            )
                        )
            except Exception as e:
                all_errors.append(
                    BeancountError(
                        source={"filename": "<plugin>", "lineno": 0},
                        message=f"Plugin '{plugin_name}.{func_name}' raised: {e}",
                        entry=None,
                    )
                )

    return list(entries), all_errors


def _sort_entries(entries: list[Directive]) -> list[Directive]:
    """Sort entries by date, then by type order, then by file location.

    This matches beancount's entry ordering.
    """
    # Type priority (lower = earlier in list for same date)
    # This matches beancount's SORT_ORDER
    type_order = {
        "RLOpen": 0,
        "RLBalance": 1,
        "RLNote": 2,
        "RLDocument": 3,
        "RLPad": 4,
        "RLTransaction": 5,
        "RLQuery": 6,
        "RLCustom": 7,
        "RLEvent": 8,
        "RLPrice": 9,
        "RLClose": 10,
        "RLCommodity": 11,
        # Beancount types (when mixed)
        "Open": 0,
        "Balance": 1,
        "Note": 2,
        "Document": 3,
        "Pad": 4,
        "Transaction": 5,
        "Query": 6,
        "Custom": 7,
        "Event": 8,
        "Price": 9,
        "Close": 10,
        "Commodity": 11,
    }

    def sort_key(entry: Directive) -> tuple:
        entry_type = type(entry).__name__
        type_priority = type_order.get(entry_type, 99)
        # Get lineno from meta if available
        lineno = entry.meta.get("lineno", 0) if entry.meta else 0
        return (entry.date, type_priority, lineno)

    return sorted(entries, key=sort_key)


def load_string(
    value: str,
    filename: str = "<string>",
) -> tuple[
    Sequence[Directive],
    Sequence[BeancountError],
    BeancountOptions,
]:
    """Load a Beancount string.

    Args:
        value: Beancount source code
        filename: Filename to use in metadata

    Returns:
        Tuple of (entries, errors, options)
    """
    engine = RustledgerEngine.get_instance()
    result = engine.load(value, filename)

    entries = directives_from_json(result.get("entries", []))
    errors = list(_errors_from_json(result.get("errors", []), filename))
    options = options_from_json(result.get("options", {}))

    # Run Python plugins if any are specified
    plugins = result.get("plugins", [])
    if plugins:
        entries, plugin_errors = _run_plugins(list(entries), plugins, options)
        errors.extend(plugin_errors)

    # Sort entries by date like beancount does
    entries = _sort_entries(entries)

    return entries, errors, options


def load_uncached(
    beancount_file_path: str,
    *,
    is_encrypted: bool = False,
) -> tuple[
    Sequence[Directive],
    Sequence[BeancountError],
    BeancountOptions,
]:
    """Load a Beancount file.

    Args:
        beancount_file_path: Path to the main beancount file
        is_encrypted: Whether the file is encrypted (not supported with rustledger)

    Returns:
        Tuple of (entries, errors, options)

    Raises:
        NotImplementedError: If file is encrypted
    """
    if is_encrypted:
        # Fall back to beancount for encrypted files
        # TODO: Could implement GPG decryption in Python
        msg = "Encrypted files not yet supported with rustledger"
        raise NotImplementedError(msg)

    main_path = Path(beancount_file_path)

    # Resolve includes at Python level
    source, included_files, _source_map = _resolve_includes(main_path)

    # Parse with rustledger
    engine = RustledgerEngine.get_instance()
    result = engine.load(source, str(main_path))

    entries = directives_from_json(result.get("entries", []))
    errors = list(_errors_from_json(result.get("errors", []), str(main_path)))
    options = options_from_json(result.get("options", {}))

    # Run Python plugins if any are specified
    plugins = result.get("plugins", [])
    if plugins:
        entries, plugin_errors = _run_plugins(list(entries), plugins, options)
        errors.extend(plugin_errors)

    # Sort entries by date like beancount does
    entries = _sort_entries(entries)

    # Ensure include list in options matches what we resolved
    options["include"] = [str(p) for p in included_files]
    options["filename"] = str(main_path)

    return entries, errors, options
