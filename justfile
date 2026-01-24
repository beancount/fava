# Rustfava Justfile
# Run `just --list` to see all available recipes

set shell := ["bash", "-euc"]
set dotenv-load

# Configuration (used by rustledger-status)
rustledger_cache := ".cache/rustledger"
target_triple := `rustc -vV 2>/dev/null | grep host | cut -d' ' -f2 || echo "unknown"`

# Default recipe - build frontend
default: frontend

# ============================================================================
# Frontend
# ============================================================================

# Build the frontend
[group('build')]
frontend:
    @if [ ! -d "frontend/node_modules" ]; then cd frontend && bun install; fi
    cd frontend && bun run build

# Install frontend dependencies
[group('build')]
frontend-deps:
    cd frontend && bun install

# ============================================================================
# Python Development
# ============================================================================

# Create and sync Python dev environment
[group('dev')]
dev: _venv
    @echo "Dev environment ready"

[private]
_venv:
    #!/usr/bin/env bash
    if [ ! -d ".venv" ] || [ "uv.lock" -nt ".venv" ] || [ "pyproject.toml" -nt ".venv" ]; then
        uv sync
        uv run pre-commit install
        touch -m .venv
    fi

# Run the example beancount files
[group('dev')]
run-example:
    @xdg-open http://localhost:3333 2>/dev/null || open http://localhost:3333 2>/dev/null || true
    BEANCOUNT_FILE= rustfava -p 3333 --debug tests/data/*.beancount

# ============================================================================
# Rustledger Build (with caching)
# ============================================================================

# Build all rustledger components (WASM + CLI) with caching
[group('rustledger')]
rustledger:
    cd desktop && bun run ensure-rustledger

# Update rustledger to latest and rebuild if needed
[group('rustledger')]
rustledger-update:
    cd desktop && bun run ensure-rustledger:update

# Force rebuild of all rustledger components
[group('rustledger')]
rustledger-rebuild:
    cd desktop && bun run ensure-rustledger:force

# Show rustledger build status
[group('rustledger')]
rustledger-status:
    #!/usr/bin/env bash
    echo "Rustledger build status:"
    echo ""

    if [ -d "{{rustledger_cache}}" ]; then
        cached_commit=$(cd "{{rustledger_cache}}" && git rev-parse HEAD)
        echo "Cached repo: {{rustledger_cache}}"
        echo "Cached commit: ${cached_commit:0:8}"

        # Check for updates
        cd "{{rustledger_cache}}"
        git fetch -q origin main 2>/dev/null || true
        upstream=$(git rev-parse origin/main 2>/dev/null || echo "unknown")
        if [ "$upstream" != "unknown" ] && [ "$upstream" != "$cached_commit" ]; then
            echo "Upstream: ${upstream:0:8} (updates available)"
        fi
        cd - > /dev/null
    else
        echo "Cached repo: not cloned"
    fi

    echo ""
    if [ -f "src/rustfava/rustledger/.wasm-version" ]; then
        echo "WASM built from: $(cat src/rustfava/rustledger/.wasm-version | head -c 8)"
    else
        echo "WASM: not built"
    fi

    marker="desktop/src-tauri/binaries/.cli-version-{{target_triple}}"
    if [ -f "$marker" ]; then
        echo "CLI ({{target_triple}}) built from: $(cat "$marker" | head -c 8)"
    else
        echo "CLI ({{target_triple}}): not built"
    fi

# ============================================================================
# Desktop App
# ============================================================================

# Run desktop app in development mode (uses latest rustledger release)
[group('desktop')]
desktop:
    cd desktop && bun run tauri:dev

# Run desktop app with bleeding-edge rustledger (main branch)
[group('desktop')]
desktop-main:
    cd desktop && bun run tauri:dev:main

# Build desktop app for release
[group('desktop')]
desktop-build:
    cd desktop && bun run tauri:build

# ============================================================================
# Testing
# ============================================================================

# Run all tests
[group('test')]
test: test-py test-js

# Run Python tests
[group('test')]
test-py:
    uv run --no-dev --group test pytest --cov=rustfava --cov-report=term-missing:skip-covered --cov-report=html --cov-fail-under=100

# Run Python tests with typeguard
[group('test')]
test-py-typeguard:
    uv run --no-dev --group test pytest --typeguard-fixtures

# Run JavaScript tests
[group('test')]
test-js: frontend-deps
    cd frontend && bun test

# Update snapshot files
[group('test')]
update-snapshots:
    uv run pytest --snapshot-update --snapshot-clean
    uv run pre-commit run -a biome-check

# ============================================================================
# Linting & Type Checking
# ============================================================================

# Run all linters
[group('lint')]
lint: frontend-deps
    uv run pre-commit run -v -a
    cd frontend && bun run tsc
    cd frontend && bun run svelte-check

# Run mypy type checking
[group('lint')]
mypy:
    uv run --no-dev --group types mypy

# ============================================================================
# Documentation
# ============================================================================

# Build documentation website
[group('docs')]
docs:
    uv run --no-dev --group docs mkdocs build -d build/docs

# Generate BQL grammar JSON
[group('docs')]
bql-grammar: _venv
    uv run --group scripts contrib/scripts.py generate-bql-grammar-json
    -uv run pre-commit run --files frontend/src/codemirror/bql-grammar.ts

# ============================================================================
# Translations
# ============================================================================

# Extract translation strings
[group('i18n')]
translations-extract: _venv
    uv run pybabel extract -F src/rustfava/translations/babel.conf -o src/rustfava/translations/messages.pot .

# Push translations to POEditor (requires POEDITOR_TOKEN)
[group('i18n')]
translations-push: _venv translations-extract
    uv run --group scripts contrib/scripts.py upload-translations

# Fetch translations from POEditor (requires POEDITOR_TOKEN)
[group('i18n')]
translations-fetch: _venv
    uv run --group scripts contrib/scripts.py download-translations

# ============================================================================
# Distribution
# ============================================================================

# Build Python distribution (sdist and wheel)
[group('dist')]
dist:
    rm -f dist/*.tar.gz dist/*.whl
    uv build

# Build PyInstaller binary
[group('dist')]
pyinstaller: frontend rustledger
    uv run --no-project --isolated --with=. --with=pyinstaller pyinstaller --clean --noconfirm contrib/pyinstaller_spec.spec
    dist/rustfava --version

# ============================================================================
# Updates
# ============================================================================

# Update all dependencies
[group('update')]
update: update-deps update-frontend-deps update-precommit update-github-actions

# Update Python dependencies
[group('update')]
update-deps:
    uv lock --upgrade

# Update frontend dependencies
[group('update')]
update-frontend-deps:
    cd frontend && bun update
    cd frontend && bun run sync-pre-commit
    touch -m frontend/node_modules

# Update tree-sitter-beancount WASM
[group('update')]
update-tree-sitter:
    curl -L -o frontend/src/codemirror/tree-sitter-beancount.wasm https://github.com/yagebu/tree-sitter-beancount/releases/download/v0.0.3/tree-sitter-beancount.wasm

# Update pre-commit hooks
[group('update')]
update-precommit:
    uv run pre-commit autoupdate

# Update GitHub Actions versions
[group('update')]
update-github-actions:
    uvx gha-update
    uvx zizmor .github/workflows/*.yml

# ============================================================================
# Release
# ============================================================================

# Pre-release tasks (BQL grammar + translations)
[group('release')]
before-release: bql-grammar translations-push translations-fetch

# ============================================================================
# Cleanup
# ============================================================================

# Remove generated files but keep caches
[group('clean')]
clean: mostlyclean
    find src/rustfava/static ! -name 'favicon.ico' -type f -exec rm -f {} +
    find src/rustfava/translations -name '*.mo' -delete
    rm -rf src/rustfava.egg-info
    rm -rf src/rustfava/translations/messages.pot

# Remove caches and generated files
[group('clean')]
mostlyclean:
    rm -rf .*cache
    rm -rf .eggs
    rm -rf .tox
    rm -rf .venv
    rm -rf build
    rm -rf dist
    rm -rf docs/api
    rm -rf htmlcov
    rm -rf frontend/node_modules
    find . -type f -name '*.py[c0]' -delete
    find . -type d -name "__pycache__" -delete

# Remove everything including rustledger cache
[group('clean')]
clean-all: clean
    rm -rf .cache
    rm -f src/rustfava/rustledger/.wasm-version
    rm -f desktop/src-tauri/binaries/.cli-version-*
    rm -f desktop/src-tauri/binaries/bean-*
    rm -f desktop/src-tauri/binaries/rledger-*
