# rustfava Desktop App

A native desktop application wrapper for rustfava, built with [Tauri](https://tauri.app/).

## Features

- Native file picker for .beancount files
- Recent files menu
- Cross-platform: macOS, Windows, Linux
- No Python/Node installation required (self-contained)

## Development

### Prerequisites

Enter the nix development shell (includes Rust, Bun, and Tauri dependencies):

```bash
nix develop
```

### Development Build

```bash
cd desktop
bun install
bun tauri dev
```

### Production Build

1. First, build the PyInstaller sidecar (the bundled rustfava server):

```bash
./desktop/build-sidecar.sh
```

2. Then build the Tauri app:

```bash
cd desktop
bun tauri build
```

Output locations:
- **Linux deb**: `src-tauri/target/release/bundle/deb/rustfava_*.deb`
- **Linux rpm**: `src-tauri/target/release/bundle/rpm/rustfava-*.rpm`
- **Linux AppImage**: `src-tauri/target/release/bundle/appimage/rustfava_*.AppImage`
- **macOS**: `src-tauri/target/release/bundle/macos/rustfava.app`
- **Windows**: `src-tauri/target/release/bundle/msi/rustfava_*.msi`

## Architecture

The app uses a "sidecar" pattern:

1. Tauri app launches and shows a file picker
2. When a file is selected, it spawns the bundled `rustfava-server` binary
3. The server runs on a random available port
4. The webview loads the rustfava web UI from localhost
5. On window close, the server process is terminated

## Files

- `src/index.html` - Launcher UI with file picker and recent files
- `src-tauri/src/main.rs` - Tauri app logic (spawn/kill sidecar)
- `src-tauri/tauri.conf.json` - Tauri configuration
- `src-tauri/binaries/` - Sidecar binaries (platform-specific)
- `build-sidecar.sh` - Script to build PyInstaller sidecar
