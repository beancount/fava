{
  description = "Rustfava - web interface for rustledger";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Python with Rustfava dependencies
        pythonEnv = pkgs.python313.withPackages (ps: with ps; [
          # Rustfava core dependencies
          flask
          flask-babel
          jinja2
          markdown2
          ply  # Used for filter syntax parsing
          watchfiles
          werkzeug
          click
          markupsafe
          cheroot  # WSGI server for rustfava CLI

          # Beancount (optional - for legacy plugin support)
          beancount
          beangulp

          # Dev/test dependencies
          pytest
          pytest-cov

          # Build dependencies
          setuptools
          wheel
          build
        ]);

      in {
        devShells.default = pkgs.mkShell {
          packages = [
            pythonEnv

            # WASM runtime for rustledger
            pkgs.wasmtime

            # Dev tools
            pkgs.just
            pkgs.jq
            pkgs.fd
            pkgs.ripgrep
            pkgs.uv  # Fast Python package manager

            # Bun for frontend build
            pkgs.bun

            # Node.js 23+ for frontend tests (required for registerHooks API)
            pkgs.nodejs_latest

            # Rust toolchain for Tauri desktop app
            pkgs.rustc
            pkgs.cargo

            # Tauri system dependencies
            pkgs.pkg-config
            pkgs.openssl
            pkgs.webkitgtk_4_1
            pkgs.libsoup_3
            pkgs.glib-networking
            pkgs.librsvg
            pkgs.gsettings-desktop-schemas
            pkgs.gtk3

          ];

          shellHook = ''
            echo "🦀 Rustfava development environment"
            echo ""
            echo "Python: $(python --version)"
            echo "Bun: $(bun --version)"
            echo "wasmtime: $(wasmtime --version)"
            echo ""
            echo "WASM file: src/rustfava/rustledger/rustledger-wasi.wasm"
            echo ""

            # GTK/GSettings environment for Tauri
            export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}:${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:$XDG_DATA_DIRS"
            export GIO_MODULE_DIR="${pkgs.glib-networking}/lib/gio/modules"

            # Create/activate venv for additional packages not in nixpkgs
            if [ ! -d ".venv" ]; then
              echo "Creating virtual environment..."
              uv venv .venv --system-site-packages
            fi
            source .venv/bin/activate

            # Install additional Python packages not in nixpkgs via uv
            if [ ! -f ".venv/.uv-installed" ]; then
              echo "Installing additional Python packages via uv..."
              uv pip install pyexcel pyexcel-ods3 pyexcel-xlsx
              # Install rustfava in editable mode for package metadata (version, etc.)
              uv pip install -e . --no-deps
              touch .venv/.uv-installed
            fi

            # Add src to PYTHONPATH for development
            export PYTHONPATH="$PWD/src:$PYTHONPATH"

            # Create a wrapper script for the rustfava CLI so tests can find it
            mkdir -p "$PWD/.dev-bin"
            cat > "$PWD/.dev-bin/rustfava" << 'WRAPPER'
#!/usr/bin/env bash
exec python -m rustfava.cli "$@"
WRAPPER
            chmod +x "$PWD/.dev-bin/rustfava"
            export PATH="$PWD/.dev-bin:$PATH"
          '';
        };
      }
    );
}
