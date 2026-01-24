"""Pydantic models for API request validation."""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class SaveSourceRequest(BaseModel):
    """Request to save source file contents."""

    file_path: str = Field(min_length=1, description="Path to source file")
    source: str = Field(description="New file contents")
    sha256sum: str = Field(
        min_length=64,
        max_length=64,
        description="SHA256 hash of original contents for conflict detection",
    )


class SaveEntrySliceRequest(BaseModel):
    """Request to save an entry source slice."""

    entry_hash: str = Field(min_length=1, description="Hash of entry to modify")
    source: str = Field(description="New entry source")
    sha256sum: str = Field(
        min_length=64,
        max_length=64,
        description="SHA256 hash of original slice for conflict detection",
    )


class FormatSourceRequest(BaseModel):
    """Request to format beancount source."""

    source: str = Field(description="Source to format")
