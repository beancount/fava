"""Loader functions for rustledger - replaces beancount.loader."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

from rustfava.rustledger.engine import RustledgerEngine
from rustfava.rustledger.options import options_from_json
from rustfava.rustledger.types import directives_from_json

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from rustfava.beans.abc import Directive
    from rustfava.beans.types import BeancountOptions
    from rustfava.helpers import BeancountError


def _compute_display_precision(entries_json: list[dict[str, Any]]) -> dict[str, int]:
    """Compute display precision from entries.

    This is a workaround until rustledger FFI returns display_precision
    from load-full command.
    """
    # Track precision counts per currency: {currency: {precision: count}}
    precision_counts: dict[str, Counter[int]] = {}

    def track_amount(amt: dict[str, Any] | None) -> None:
        if not amt:
            return
        number_str = amt.get("number", "")
        currency = amt.get("currency", "")
        if not number_str or not currency:
            return
        # Calculate precision from decimal places
        if "." in str(number_str):
            precision = len(str(number_str).split(".")[-1])
        else:
            precision = 0
        if currency not in precision_counts:
            precision_counts[currency] = Counter()
        precision_counts[currency][precision] += 1

    for entry in entries_json:
        entry_type = entry.get("type", "")

        if entry_type == "transaction":
            for posting in entry.get("postings", []):
                track_amount(posting.get("units"))
                if posting.get("cost"):
                    cost = posting["cost"]
                    track_amount({"number": cost.get("number"), "currency": cost.get("currency")})
                track_amount(posting.get("price"))

        elif entry_type == "balance":
            track_amount(entry.get("amount"))

        elif entry_type == "price":
            track_amount(entry.get("amount"))

    # Get most common precision for each currency
    result = {}
    for currency, counts in precision_counts.items():
        if counts:
            result[currency] = counts.most_common(1)[0][0]

    return result


def _errors_from_json(
    errors_json: list[dict[str, Any]],
    filename: str = "<unknown>",
) -> list[BeancountError]:
    """Convert rustledger errors to Fava BeancountError format."""
    from rustfava.helpers import BeancountError

    result = []
    for err in errors_json:
        # Handle both old format (source dict) and new format (line field)
        if "source" in err:
            source = err["source"]
            err_filename = source.get("filename", filename)
            err_lineno = source.get("lineno", 0)
        else:
            err_filename = err.get("filename", filename)
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


def _run_plugins(
    entries: list[Directive],
    plugins: list[dict[str, Any]],
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
    import importlib

    from rustfava.helpers import BeancountError

    all_errors: list[BeancountError] = []

    for plugin_spec in plugins:
        plugin_name = plugin_spec.get("name", "")
        plugin_config = plugin_spec.get("config")

        if not plugin_name:
            continue

        # Skip beancount.plugins.auto_accounts - handled natively by rustledger
        if plugin_name == "beancount.plugins.auto_accounts":
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
                if plugin_config is not None:
                    entries, plugin_errors = plugin_fn(entries, plugin_config)
                else:
                    entries, plugin_errors = plugin_fn(entries, options)

                # Convert any plugin errors to our error format
                for err in plugin_errors:
                    if isinstance(err, BeancountError):
                        all_errors.append(err)
                    else:
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

    entries = list(directives_from_json(result.get("entries", [])))
    errors = list(_errors_from_json(result.get("errors", []), filename))
    options = options_from_json(result.get("options", {}))

    # Run Python plugins if any are specified
    plugins = result.get("plugins", [])
    if plugins:
        entries, plugin_errors = _run_plugins(entries, plugins, options)
        errors.extend(plugin_errors)

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

    Uses rustledger's load-full command which handles:
    - Include resolution with cycle detection
    - Path security (prevents path traversal)
    - GPG decryption for encrypted files
    - Native plugin execution (auto_accounts)
    - Entry sorting

    Args:
        beancount_file_path: Path to the main beancount file
        is_encrypted: Ignored - rustledger handles GPG decryption

    Returns:
        Tuple of (entries, errors, options)
    """
    del is_encrypted  # Rustledger handles GPG decryption automatically

    main_path = Path(beancount_file_path)
    engine = RustledgerEngine.get_instance()

    # Use load_full with auto_accounts plugin for sorting and account generation
    result = engine.load_full(str(main_path), plugins=["auto_accounts"])

    entries_json = result.get("entries", [])

    # Compute display_precision if not provided by FFI (workaround)
    options_json = result.get("options", {})
    if not options_json.get("display_precision"):
        options_json["display_precision"] = _compute_display_precision(entries_json)

    entries = directives_from_json(entries_json)
    errors = list(_errors_from_json(result.get("errors", []), str(main_path)))
    options = options_from_json(options_json)

    # Set include list and filename in options
    options["include"] = result.get("loaded_files", [str(main_path)])
    options["filename"] = str(main_path)

    return entries, errors, options
