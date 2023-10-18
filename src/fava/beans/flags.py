"""Beancount entry flags."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypeAlias

    Flag: TypeAlias = str

FLAG_CONVERSIONS = "C"
FLAG_MERGING = "M"
FLAG_OKAY = "*"
FLAG_PADDING = "P"
FLAG_RETURNS = "R"
FLAG_SUMMARIZE = "S"
FLAG_TRANSFER = "T"
FLAG_UNREALIZED = "U"
FLAG_WARNING = "!"
