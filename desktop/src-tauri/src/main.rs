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
    tabs: Mutex<HashMap<String, TabInfo>>,  // tab_id -> TabInfo
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

/// Generate a unique tab ID
fn generate_tab_id(state: &State<AppState>) -> String {
    let mut next_id = state.next_id.lock().unwrap();
    let id = format!("tab_{}", *next_id);
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
    let tab_id = generate_tab_id(&state);
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

/// Kill all servers on shutdown
fn cleanup_all_tabs(state: &AppState) {
    let mut tabs = state.tabs.lock().unwrap();
    for (_, info) in tabs.drain() {
        let _ = info.child.kill();
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
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
                    // Emit event to frontend to trigger file picker
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
                "quit" => {
                    app.exit(0);
                }
                _ => {}
            }
        })
        .invoke_handler(tauri::generate_handler![open_file, close_tab, get_tabs])
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                // Kill all servers when the window is closed
                if let Some(state) = window.try_state::<AppState>() {
                    cleanup_all_tabs(&state);
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("Error while running rustfava desktop");
}
