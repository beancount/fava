// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::collections::HashMap;
use std::net::TcpListener;
use std::sync::Mutex;
use tauri::{AppHandle, Emitter, Manager, State};
use tauri::menu::{Menu, MenuItem, Submenu};
use tauri_plugin_shell::process::CommandChild;
use tauri_plugin_shell::ShellExt;

/// Represents an open tab with its server process
struct TabInfo {
    path: String,
    port: u16,
    child: CommandChild,
}

/// Holds the state of all open tabs
struct AppState {
    tabs: Mutex<HashMap<String, TabInfo>>,
    next_id: Mutex<u32>,
}

/// Find an available port by binding to port 0
fn find_free_port() -> u16 {
    TcpListener::bind("127.0.0.1:0")
        .expect("Failed to bind to port 0")
        .local_addr()
        .expect("Failed to get local address")
        .port()
}

/// Get the path to the bundled example beancount file
#[tauri::command]
fn get_example_file_path(app: AppHandle) -> Result<String, String> {
    // In development, use the path relative to the project root
    // In production, this would be bundled as a resource
    let resource_dir = app.path().resource_dir()
        .map_err(|e| format!("Failed to get resource dir: {}", e))?;

    // Try bundled resource first
    let bundled_path = resource_dir.join("examples").join("example.beancount");
    if bundled_path.exists() {
        return Ok(bundled_path.to_string_lossy().to_string());
    }

    // Fall back to development path (relative to desktop/src-tauri)
    let dev_path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent() // desktop/
        .and_then(|p| p.parent()) // project root
        .map(|p| p.join("contrib").join("examples").join("example.beancount"));

    if let Some(path) = dev_path {
        if path.exists() {
            return Ok(path.to_string_lossy().to_string());
        }
    }

    Err("Example file not found".to_string())
}

/// Get terminal environment with sidecar binaries in PATH
/// Returns all inherited env vars with PATH modified to include sidecar directory
#[tauri::command]
fn get_terminal_env(app: AppHandle) -> Result<std::collections::HashMap<String, String>, String> {
    // Get the sidecar directory
    let resource_dir = app.path().resource_dir()
        .map_err(|e| format!("Failed to get resource dir: {}", e))?;

    // Collect all current environment variables
    let mut env: std::collections::HashMap<String, String> = std::env::vars().collect();

    // Prepend sidecar directory to PATH
    let current_path = env.get("PATH").cloned().unwrap_or_default();
    let new_path = format!("{}:{}", resource_dir.to_string_lossy(), current_path);
    env.insert("PATH".to_string(), new_path);

    // Add marker for sidecar directory
    env.insert("RUSTFAVA_SIDECAR_DIR".to_string(), resource_dir.to_string_lossy().to_string());

    Ok(env)
}

/// Generate a unique ID
fn generate_id(state: &State<AppState>, prefix: &str) -> String {
    let mut next_id = state.next_id.lock().unwrap();
    let id = format!("{}_{}", prefix, *next_id);
    *next_id += 1;
    id
}

/// Open a beancount file in a new tab
#[tauri::command]
fn open_file(
    app: AppHandle,
    path: String,
    state: State<AppState>,
) -> Result<serde_json::Value, String> {
    // Check if file is already open
    {
        let tabs = state.tabs.lock().unwrap();
        for (tab_id, info) in tabs.iter() {
            if info.path == path {
                return Ok(serde_json::json!({
                    "tab_id": tab_id,
                    "url": format!("http://127.0.0.1:{}", info.port),
                    "path": path,
                    "already_open": true
                }));
            }
        }
    }

    // Find a free port
    let port = find_free_port();

    // Spawn the sidecar binary
    let sidecar = app
        .shell()
        .sidecar("rustfava-server")
        .map_err(|e| format!("Failed to create sidecar command: {}", e))?
        .args([&path, "-p", &port.to_string()]);

    let (mut _rx, child) = sidecar
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

    // Generate tab ID and store
    let tab_id = generate_id(&state, "tab");
    let url = format!("http://127.0.0.1:{}", port);

    state.tabs.lock().unwrap().insert(
        tab_id.clone(),
        TabInfo {
            path: path.clone(),
            port,
            child,
        },
    );

    Ok(serde_json::json!({
        "tab_id": tab_id,
        "url": url,
        "path": path,
        "already_open": false
    }))
}

/// Close a tab and kill its server
#[tauri::command]
fn close_tab(tab_id: String, state: State<AppState>) -> Result<(), String> {
    let mut tabs = state.tabs.lock().unwrap();
    if let Some(info) = tabs.remove(&tab_id) {
        let _ = info.child.kill();
        Ok(())
    } else {
        Err(format!("Tab not found: {}", tab_id))
    }
}

/// Get all open tabs
#[tauri::command]
fn get_tabs(state: State<AppState>) -> Vec<serde_json::Value> {
    let tabs = state.tabs.lock().unwrap();
    tabs.iter()
        .map(|(id, info)| {
            serde_json::json!({
                "tab_id": id,
                "url": format!("http://127.0.0.1:{}", info.port),
                "path": info.path,
                "name": info.path.split('/').last().unwrap_or(&info.path)
            })
        })
        .collect()
}

/// Get the user's default shell and launch arguments
#[tauri::command]
fn get_default_shell() -> serde_json::Value {
    let (shell, args) = get_shell_and_args();
    serde_json::json!({
        "shell": shell,
        "args": args
    })
}

#[cfg(any(target_os = "macos", target_os = "linux"))]
fn get_shell_and_args() -> (String, Vec<String>) {
    // Get user's actual login shell from system (not $SHELL which may be overridden by nix/etc)
    let shell = get_login_shell().unwrap_or_else(|| {
        // Fall back to $SHELL, then platform default
        std::env::var("SHELL").unwrap_or_else(|_| {
            if cfg!(target_os = "macos") {
                "/bin/zsh".to_string()
            } else {
                "/bin/bash".to_string()
            }
        })
    });

    // Interactive mode - PTY makes it interactive, rc files will be sourced
    (shell, vec!["-i".to_string()])
}

#[cfg(target_os = "linux")]
fn get_login_shell() -> Option<String> {
    // Use getent passwd to get the user's actual login shell
    let user = std::env::var("USER").ok()?;
    let output = std::process::Command::new("getent")
        .args(["passwd", &user])
        .output()
        .ok()?;

    if output.status.success() {
        let line = String::from_utf8_lossy(&output.stdout);
        // Format: username:x:uid:gid:gecos:home:shell
        let shell = line.trim().split(':').last()?.to_string();
        if !shell.is_empty() && std::path::Path::new(&shell).exists() {
            return Some(shell);
        }
    }
    None
}

#[cfg(target_os = "macos")]
fn get_login_shell() -> Option<String> {
    // Use dscl to get the user's login shell on macOS
    let user = std::env::var("USER").ok()?;
    let output = std::process::Command::new("dscl")
        .args([".", "-read", &format!("/Users/{}", user), "UserShell"])
        .output()
        .ok()?;

    if output.status.success() {
        let line = String::from_utf8_lossy(&output.stdout);
        // Format: UserShell: /bin/zsh
        let shell = line.trim().split_whitespace().last()?.to_string();
        if !shell.is_empty() && std::path::Path::new(&shell).exists() {
            return Some(shell);
        }
    }
    None
}

#[cfg(target_os = "windows")]
fn get_shell_and_args() -> (String, Vec<String>) {
    // Try PowerShell 7 (pwsh), then PowerShell 5, then cmd
    let shell = if std::process::Command::new("pwsh").arg("--version").output().is_ok() {
        "pwsh.exe".to_string()
    } else if std::process::Command::new("powershell").arg("-Command").arg("exit").output().is_ok() {
        "powershell.exe".to_string()
    } else {
        std::env::var("COMSPEC").unwrap_or_else(|_| "cmd.exe".to_string())
    };

    let args = if shell.contains("powershell") || shell.contains("pwsh") {
        vec!["-NoExit".to_string()]
    } else {
        vec![]
    };

    (shell, args)
}

/// Kill all servers on shutdown
fn cleanup_all(state: &AppState) {
    let mut tabs = state.tabs.lock().unwrap();
    for (_, info) in tabs.drain() {
        let _ = info.child.kill();
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_pty::init())
        .manage(AppState {
            tabs: Mutex::new(HashMap::new()),
            next_id: Mutex::new(1),
        })
        .setup(|app| {
            // Create menu
            let file_menu = Submenu::with_items(
                app,
                "File",
                true,
                &[
                    &MenuItem::with_id(app, "open", "Open File...", true, Some("CmdOrCtrl+O"))?,
                    &MenuItem::with_id(app, "close_tab", "Close Tab", true, Some("CmdOrCtrl+W"))?,
                    &MenuItem::with_id(app, "quit", "Quit", true, Some("CmdOrCtrl+Q"))?,
                ],
            )?;

            let edit_menu = Submenu::with_items(
                app,
                "Edit",
                true,
                &[
                    &MenuItem::with_id(app, "undo", "Undo", true, Some("CmdOrCtrl+Z"))?,
                    &MenuItem::with_id(app, "redo", "Redo", true, Some("CmdOrCtrl+Shift+Z"))?,
                    &MenuItem::with_id(app, "cut", "Cut", true, Some("CmdOrCtrl+X"))?,
                    &MenuItem::with_id(app, "copy", "Copy", true, Some("CmdOrCtrl+C"))?,
                    &MenuItem::with_id(app, "paste", "Paste", true, Some("CmdOrCtrl+V"))?,
                    &MenuItem::with_id(app, "select_all", "Select All", true, Some("CmdOrCtrl+A"))?,
                ],
            )?;

            let view_menu = Submenu::with_items(
                app,
                "View",
                true,
                &[
                    &MenuItem::with_id(app, "reload", "Reload", true, Some("CmdOrCtrl+R"))?,
                    &MenuItem::with_id(app, "toggle_terminal", "Toggle Terminal", true, Some("CmdOrCtrl+`"))?,
                    &MenuItem::with_id(app, "zoom_in", "Zoom In", true, Some("CmdOrCtrl+Plus"))?,
                    &MenuItem::with_id(app, "zoom_out", "Zoom Out", true, Some("CmdOrCtrl+Minus"))?,
                    &MenuItem::with_id(app, "zoom_reset", "Reset Zoom", true, Some("CmdOrCtrl+0"))?,
                ],
            )?;

            let menu = Menu::with_items(app, &[&file_menu, &edit_menu, &view_menu])?;
            app.set_menu(menu)?;

            Ok(())
        })
        .on_menu_event(|app, event| {
            match event.id().as_ref() {
                "open" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.emit("menu-open-file", ());
                    }
                }
                "close_tab" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.emit("menu-close-tab", ());
                    }
                }
                "reload" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.emit("menu-reload", ());
                    }
                }
                "toggle_terminal" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.emit("menu-toggle-terminal", ());
                    }
                }
                "quit" => {
                    app.exit(0);
                }
                _ => {}
            }
        })
        .invoke_handler(tauri::generate_handler![
            open_file,
            close_tab,
            get_tabs,
            get_default_shell,
            get_terminal_env,
            get_example_file_path
        ])
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                if let Some(state) = window.try_state::<AppState>() {
                    cleanup_all(&state);
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("Error while running rustfava desktop");
}
