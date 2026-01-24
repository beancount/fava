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
          ply
          simplejson
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
