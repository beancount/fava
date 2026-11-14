"""Tests for the external editor command and project config loading."""

from __future__ import annotations

import subprocess
from http import HTTPStatus
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner

from fava.application import create_app
from fava.cli import main
from fava.config import FavaProjectConfig
from fava.config import load_project_config
from fava.config import ProjectConfigError
from fava.core.fava_options import parse_options

from .test_json_api import assert_api_error
from .test_json_api import assert_api_success

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask
    from flask.testing import FlaskClient

    from fava.beans.abc import Custom


def test_start_with_valid_config_file(
    test_data_dir: Path, tmp_path: Path
) -> None:
    """A valid config file is loaded at startup."""
    config = tmp_path / "pyproject.toml"
    config.write_text(
        """
[tool.fava]
external-editor-command = ["echo", "${file}:${line}"]
""".strip(),
        encoding="utf-8",
    )

    app = create_app(
        [test_data_dir / "example.beancount"],
        config_file=str(config),
        load=True,
    )
    assert app.config["LEDGERS"].ledgers[0].use_external_editor


def test_start_with_invalid_config_file_fails(
    test_data_dir: Path,
    tmp_path: Path,
) -> None:
    """An invalid config file fails startup."""
    config = tmp_path / "pyproject.toml"
    config.write_text(
        """
[tool.fava]
external-editor-command = "echo ${file}:${line}"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ProjectConfigError):
        create_app(
            [test_data_dir / "example.beancount"],
            config_file=str(config),
        )


def test_load_project_config_without_tool_returns_default(
    tmp_path: Path,
) -> None:
    config = tmp_path / "pyproject.toml"
    config.write_text("[project]\nname = 'example'\n", encoding="utf-8")

    loaded = load_project_config(str(config))

    assert loaded == FavaProjectConfig()
    assert not loaded.use_external_editor


def test_load_project_config_without_tool_fava_returns_default(
    tmp_path: Path,
) -> None:
    config = tmp_path / "pyproject.toml"
    config.write_text("[tool]\n", encoding="utf-8")

    loaded = load_project_config(str(config))

    assert loaded == FavaProjectConfig()
    assert not loaded.use_external_editor


def test_load_project_config_invalid_tool_table(tmp_path: Path) -> None:
    config = tmp_path / "pyproject.toml"
    config.write_text("tool = 'invalid'\n", encoding="utf-8")

    with pytest.raises(ProjectConfigError, match="`tool` must be a table"):
        load_project_config(str(config))


def test_load_project_config_invalid_tool_fava_table(tmp_path: Path) -> None:
    config = tmp_path / "pyproject.toml"
    config.write_text("[tool]\nfava = 'invalid'\n", encoding="utf-8")

    with pytest.raises(
        ProjectConfigError,
        match=r"`tool\.fava` must be a table",
    ):
        load_project_config(str(config))


def test_load_project_config_invalid_toml(tmp_path: Path) -> None:
    config = tmp_path / "pyproject.toml"
    config.write_text("[tool.fava\n", encoding="utf-8")

    with pytest.raises(ProjectConfigError):
        load_project_config(str(config))


def test_cli_invalid_config_file(test_data_dir: Path, tmp_path: Path) -> None:
    config = tmp_path / "pyproject.toml"
    config.write_text(
        """
[tool.fava]
external-editor-command = "echo ${file}:${line}"
""".strip(),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            str(test_data_dir / "example.beancount"),
            "--config-file",
            str(config),
        ],
    )

    assert result.exit_code != 0
    assert "Failed to load config file" in result.output


def test_fava_options_use_external_editor_unknown(
    load_doc_custom_entries: list[Custom],
) -> None:
    """
    2016-04-14 custom "fava-option" "use-external-editor" "true"
    """
    _options, errors = parse_options(load_doc_custom_entries)

    assert len(errors) == 1
    assert "Unknown option `use_external_editor`" in errors[0].message


def test_fava_options_external_editor_command_unknown(
    load_doc_custom_entries: list[Custom],
) -> None:
    """
    2016-04-14 custom "fava-option" "external-editor-command" "x"
    """
    _options, errors = parse_options(load_doc_custom_entries)

    assert len(errors) == 1
    assert "Unknown option `external_editor_command`" in errors[0].message


def test_api_open_in_editor_requires_command(
    app: Flask, test_client: FlaskClient
) -> None:
    ledger = app.config["LEDGERS"]["example"]
    file_path = ledger.options["include"][0]

    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": file_path, "line": "10"},
    )
    assert_api_error(
        response,
        "No external editor command configured.",
        status=HTTPStatus.BAD_REQUEST,
    )


def test_api_open_in_editor_requires_project_config(
    app: Flask,
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = app.config["LEDGERS"]["example"]
    file_path = ledger.options["include"][0]
    monkeypatch.setattr(ledger, "project_config", None)

    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": file_path, "line": "10"},
    )
    assert_api_error(
        response,
        "No external editor command configured.",
        status=HTTPStatus.BAD_REQUEST,
    )


def test_api_open_in_editor_executes_command(
    app: Flask,
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = app.config["LEDGERS"]["example"]
    file_path = ledger.options["include"][0]
    monkeypatch.setattr(
        ledger.project_config,
        "external_editor_command",
        ["echo", "${file}:${line}"],
    )

    calls: list[list[str]] = []

    def fake_check_call(args: list[str]) -> None:
        calls.append(args)

    monkeypatch.setattr(subprocess, "check_call", fake_check_call)

    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": file_path, "line": "42"},
    )
    assert_api_success(response)
    assert calls == [[which("echo"), f"{file_path}:42"]]

    other_path = Path(file_path).parent / "not_included.beancount"
    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": str(other_path), "line": "1"},
    )
    assert_api_error(
        response,
        f"Not a Beancount source file: '{other_path}'.",
        status=HTTPStatus.BAD_REQUEST,
    )
    assert len(calls) == 1


def test_api_open_in_editor_invalid_line(
    app: Flask,
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = app.config["LEDGERS"]["example"]
    file_path = ledger.options["include"][0]
    monkeypatch.setattr(
        ledger.project_config,
        "external_editor_command",
        ["echo", "${file}:${line}"],
    )

    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": file_path, "line": "not-a-number"},
    )
    assert_api_error(
        response,
        "Invalid external editor command: line must be an integer",
        status=HTTPStatus.BAD_REQUEST,
    )


def test_api_open_in_editor_empty_command(
    app: Flask,
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = app.config["LEDGERS"]["example"]
    file_path = ledger.options["include"][0]
    monkeypatch.setattr(
        ledger.project_config,
        "external_editor_command",
        [],
    )

    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": file_path, "line": "10"},
    )
    assert_api_error(
        response,
        "Invalid external editor command: command is empty",
        status=HTTPStatus.BAD_REQUEST,
    )


def test_api_open_in_editor_empty_command_executable(
    app: Flask,
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = app.config["LEDGERS"]["example"]
    file_path = ledger.options["include"][0]
    monkeypatch.setattr(
        ledger.project_config,
        "external_editor_command",
        ["", "${file}:${line}"],
    )

    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": file_path, "line": "10"},
    )
    assert_api_error(
        response,
        "Invalid external editor command: command is empty",
        status=HTTPStatus.BAD_REQUEST,
    )


def test_api_open_in_editor_missing_variable(
    app: Flask,
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = app.config["LEDGERS"]["example"]
    file_path = ledger.options["include"][0]
    monkeypatch.setattr(
        ledger.project_config,
        "external_editor_command",
        ["echo", "${missing}"],
    )

    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": file_path, "line": "10"},
    )
    assert_api_error(
        response,
        "Invalid external editor command: missing variable 'missing'",
        status=HTTPStatus.BAD_REQUEST,
    )


def test_api_open_in_editor_invalid_placeholder(
    app: Flask,
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = app.config["LEDGERS"]["example"]
    file_path = ledger.options["include"][0]
    monkeypatch.setattr(
        ledger.project_config,
        "external_editor_command",
        ["echo", "file$"],
    )

    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": file_path, "line": "10"},
    )
    assert_api_error(
        response,
        "Invalid external editor command: "
        "Invalid placeholder in string: line 1, col 5",
        status=HTTPStatus.BAD_REQUEST,
    )


def test_api_open_in_editor_requires_file(
    app: Flask,
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    ledger = app.config["LEDGERS"]["example"]
    monkeypatch.setitem(ledger.options, "include", [str(tmp_path)])
    monkeypatch.setattr(
        ledger.project_config,
        "external_editor_command",
        ["echo", "${file}:${line}"],
    )

    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": str(tmp_path), "line": "10"},
    )
    assert_api_error(
        response,
        f"Not a file: '{tmp_path}'",
        status=HTTPStatus.UNPROCESSABLE_ENTITY,
    )


def test_api_open_in_editor_command_failure(
    app: Flask,
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = app.config["LEDGERS"]["example"]
    file_path = ledger.options["include"][0]
    monkeypatch.setattr(
        ledger.project_config,
        "external_editor_command",
        ["echo", "${file}:${line}"],
    )

    def fake_check_call(args: list[str]) -> None:
        raise subprocess.CalledProcessError(1, args, stderr="boom")

    monkeypatch.setattr(subprocess, "check_call", fake_check_call)

    response = test_client.put(
        "/example/api/open_in_editor",
        json={"file_path": file_path, "line": "10"},
    )
    assert_api_error(
        response,
        "Failed to run external editor command: boom.",
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )
