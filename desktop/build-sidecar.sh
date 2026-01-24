#!/bin/bash
# Build the rustfava PyInstaller sidecar binary for Tauri
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BINARIES_DIR="$SCRIPT_DIR/src-tauri/binaries"

echo "Building rustfava sidecar binary..."
cd "$PROJECT_ROOT"

# Build with PyInstaller
pyinstaller contrib/pyinstaller_spec.spec --noconfirm

# Create binaries directory
mkdir -p "$BINARIES_DIR"

# Determine target triple and copy binary
case "$(uname -s)" in
  Darwin*)
    case "$(uname -m)" in
      arm64)
        TARGET="aarch64-apple-darwin"
        ;;
      x86_64)
        TARGET="x86_64-apple-darwin"
        ;;
      *)
        echo "Unsupported macOS architecture: $(uname -m)"
        exit 1
        ;;
    esac
    BINARY="dist/rustfava"
    ;;
  Linux*)
    case "$(uname -m)" in
      x86_64)
        TARGET="x86_64-unknown-linux-gnu"
        ;;
      aarch64)
        TARGET="aarch64-unknown-linux-gnu"
        ;;
      *)
        echo "Unsupported Linux architecture: $(uname -m)"
        exit 1
        ;;
    esac
    BINARY="dist/rustfava"
    ;;
  MINGW*|MSYS*|CYGWIN*)
    TARGET="x86_64-pc-windows-msvc"
    BINARY="dist/rustfava.exe"
    ;;
  *)
    echo "Unsupported operating system: $(uname -s)"
    exit 1
    ;;
esac

DEST="$BINARIES_DIR/rustfava-server-$TARGET"
if [[ "$TARGET" == *"windows"* ]]; then
  DEST="$DEST.exe"
fi

echo "Copying $BINARY to $DEST"
cp "$BINARY" "$DEST"
chmod +x "$DEST"

echo "Sidecar binary built successfully: $DEST"
