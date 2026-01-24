// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::net::TcpListener;
use std::sync::Mutex;
use tauri::{AppHandle, Manager, State};
use tauri_plugin_shell::process::CommandChild;
use tauri_plugin_shell::ShellExt;

/// Holds the state of the running server process
struct ServerState {
    child: Mutex<Option<CommandChild>>,
    port: Mutex<u16>,
}

/// Find an available port by binding to port 0
fn find_free_port() -> u16 {
    TcpListener::bind("127.0.0.1:0")
        .expect("Failed to bind to port 0")
        .local_addr()
        .expect("Failed to get local address")
        .port()
}

/// Kill the existing server process if running
fn kill_existing_server(state: &State<ServerState>) {
    if let Some(child) = state.child.lock().unwrap().take() {
        let _ = child.kill();
    }
}

/// Open a beancount file and start the rustfava server
#[tauri::command]
fn open_file(
    app: AppHandle,
    path: String,
    state: State<ServerState>,
) -> Result<String, String> {
    // Kill any existing server
    kill_existing_server(&state);

    // Find a free port
    let port = find_free_port();
    *state.port.lock().unwrap() = port;

    // Spawn the sidecar binary
    let sidecar = app
        .shell()
        .sidecar("rustfava-server")
        .map_err(|e| format!("Failed to create sidecar command: {}", e))?
        .args([&path, "-p", &port.to_string()]);

    let (mut _rx, child) = sidecar
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

    // Store the child process handle
    *state.child.lock().unwrap() = Some(child);

    Ok(format!("http://127.0.0.1:{}", port))
}

/// Get the current server URL
#[tauri::command]
fn get_server_url(state: State<ServerState>) -> Option<String> {
    let port = *state.port.lock().unwrap();
    if port > 0 {
        Some(format!("http://127.0.0.1:{}", port))
    } else {
        None
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .manage(ServerState {
            child: Mutex::new(None),
            port: Mutex::new(0),
        })
        .invoke_handler(tauri::generate_handler![open_file, get_server_url])
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                // Kill the server when the window is closed
                if let Some(state) = window.try_state::<ServerState>() {
                    if let Some(child) = state.child.lock().unwrap().take() {
                        let _ = child.kill();
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("Error while running rustfava desktop");
}
