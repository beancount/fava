"""Specify types for the flask application context."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import g as flask_g

if TYPE_CHECKING:  # pragma: no cover
    from fava._ctx_globals_class import Context


g: Context = flask_g  # type: ignore[assignment]
