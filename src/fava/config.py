"""Project configuration loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomli
from dacite import Config
from dacite import DaciteError
from dacite import from_dict


class ProjectConfigError(ValueError):
    """Error while loading project configuration."""


@dataclass
class FavaProjectConfig:
    """Configuration loaded from ``[tool.fava]`` in ``pyproject.toml``."""

    external_editor_command: list[str] | None = None


def _kebab_to_snake(key: str) -> str:
    return key.replace("-", "_")


def _normalize_keys(data: dict[str, Any]) -> dict[str, Any]:
    return {_kebab_to_snake(key): value for key, value in data.items()}


def load_project_config(config_file: str | None) -> FavaProjectConfig:
    """Load a project configuration from ``pyproject.toml``.

    Args:
        config_file: Path to the ``pyproject.toml`` file.

    Returns:
        Parsed config.

    Raises:
        ProjectConfigError: If config cannot be parsed or validated.
    """
    if not config_file:
        return FavaProjectConfig()

    try:
        with Path(config_file).open("rb") as file_obj:
            config_data = tomli.load(file_obj)
    except (OSError, tomli.TOMLDecodeError) as err:
        raise ProjectConfigError(str(err)) from err

    tool_data = config_data.get("tool")
    if tool_data is None:
        return FavaProjectConfig()
    if not isinstance(tool_data, dict):
        msg = "`tool` must be a table"
        raise ProjectConfigError(msg)

    fava_data = tool_data.get("fava")
    if fava_data is None:
        return FavaProjectConfig()
    if not isinstance(fava_data, dict):
        msg = "`tool.fava` must be a table"
        raise ProjectConfigError(msg)

    try:
        return from_dict(
            data_class=FavaProjectConfig,
            data=_normalize_keys(fava_data),
            config=Config(strict=True),
        )
    except DaciteError as err:
        raise ProjectConfigError(str(err)) from err
