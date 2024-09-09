"""Fava's extension system."""

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from functools import cached_property
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import jinja2
from flask import current_app

from fava.helpers import BeancountError

if TYPE_CHECKING:  # pragma: no cover
    from typing import Callable
    from typing import TypeVar

    from flask.wrappers import Response

    from fava.beans.abc import Directive
    from fava.core import FavaLedger


class FavaExtensionError(BeancountError):
    """Error in one of Fava's extensions."""


class JinjaLoaderMissingError(ValueError):  # noqa: D101
    def __init__(self) -> None:
        super().__init__("Expected Flask app to have jinja_loader.")


class FavaExtensionBase:
    """Base class for extensions for Fava.

    Any extension should inherit from this class. :func:`find_extension` will
    discover all subclasses of this class in the specified modules.
    """

    #: Name for a HTML report for this extension.
    report_title: str | None = None

    #: Whether this extension includes a Javascript module.
    has_js_module: bool = False

    config: Any

    endpoints: dict[tuple[str, str], Callable[[FavaExtensionBase], Any]]

    def __init__(self, ledger: FavaLedger, config: str | None = None) -> None:
        """Initialise extension.

        Args:
            ledger: Input ledger file.
            config: Configuration options string passed from the
                    beancount file's 'fava-extension' line.
        """
        self.endpoints = {}

        # Go through each of the subclass's functions to find the ones
        # marked as endpoints by @extension_endpoint
        for _, func in inspect.getmembers(self.__class__, inspect.isfunction):
            if hasattr(func, "endpoint_key"):
                name, methods = func.endpoint_key
                for method in methods:
                    self.endpoints[name, method] = func

        self.ledger = ledger
        try:
            self.config = ast.literal_eval(config) if config else None
        except ValueError:
            self.config = None

    @property
    def name(self) -> str:
        """Unique name of this extension."""
        return self.__class__.__qualname__

    @property
    def extension_dir(self) -> Path:
        """Directory to look for templates directory and Javascript code."""
        return Path(inspect.getfile(self.__class__)).parent

    @cached_property
    def jinja_env(self) -> jinja2.Environment:
        """Jinja env for this extension."""
        if not current_app.jinja_loader:
            raise JinjaLoaderMissingError
        ext_loader = jinja2.FileSystemLoader(self.extension_dir / "templates")
        loader = jinja2.ChoiceLoader([ext_loader, current_app.jinja_loader])
        return current_app.jinja_env.overlay(loader=loader)

    def after_load_file(self) -> None:
        """Run after a ledger file has been loaded."""

    def before_request(self) -> None:
        """Run before each client request."""

    def after_entry_modified(self, entry: Directive, new_lines: str) -> None:
        """Run after an `entry` has been modified."""

    def after_insert_entry(self, entry: Directive) -> None:
        """Run after an `entry` has been inserted."""

    def after_delete_entry(self, entry: Directive) -> None:
        """Run after an `entry` has been deleted."""

    def after_insert_metadata(
        self,
        entry: Directive,
        key: str,
        value: str,
    ) -> None:
        """Run after metadata (key: value) was added to an entry."""

    def after_write_source(self, path: str, source: str) -> None:
        """Run after `source` has been written to path."""


def find_extensions(
    base_path: Path,
    name: str,
) -> tuple[list[type[FavaExtensionBase]], list[FavaExtensionError]]:
    """Find extensions in a module.

    Args:
        base_path: The module can be relative to this path.
        name: The name of the module containing the extensions.

    Returns:
        A tuple (classes, errors) where classes is a list of subclasses of
        :class:`FavaExtensionBase` found in ``name``.
    """
    classes = []

    sys.path.insert(0, str(base_path))
    try:
        module = importlib.import_module(name)
    except ImportError as err:
        error = FavaExtensionError(
            None,
            f'Importing module "{name}" failed.\nError: "{err.msg}"',
            None,
        )
        return (
            [],
            [error],
        )
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, FavaExtensionBase) and obj != FavaExtensionBase:
            classes.append(obj)
    sys.path.pop(0)

    if not classes:
        error = FavaExtensionError(
            None,
            f'Module "{name}" contains no extensions.',
            None,
        )
        return (
            [],
            [error],
        )

    return classes, []


if TYPE_CHECKING:  # pragma: no cover
    T = TypeVar("T", bound=FavaExtensionBase)


def extension_endpoint(
    func_or_endpoint_name: (Callable[[T], Any] | str | None) = None,
    methods: list[str] | None = None,
) -> (
    Callable[[T], Response]
    | Callable[
        [Callable[[T], Response]],
        Callable[[T], Response],
    ]
):
    """Decorator to mark a function as an endpoint.

    Can be used as `@extension_endpoint` or
    `@extension_endpoint(endpoint_name, methods)`.

    When used as @extension_endpoint, the endpoint name is the name of the
    function and methods is "GET".

    When used as @extension_endpoint(endpoint_name, methods), the given
    endpoint name and methods are used, but both are optional. If
    endpoint_name is None, default to the function name, and if methods
    is None, default to "GET".
    """
    endpoint_name = (
        func_or_endpoint_name
        if isinstance(func_or_endpoint_name, str)
        else None
    )

    def decorator(
        func: Callable[[T], Response],
    ) -> Callable[[T], Response]:
        f: Any = func
        f.endpoint_key = (
            endpoint_name or func.__name__,
            methods or ["GET"],
        )
        return func

    return (
        decorator(func_or_endpoint_name)
        if callable(func_or_endpoint_name)
        else decorator
    )
