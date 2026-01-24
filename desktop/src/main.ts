import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { open } from "@tauri-apps/plugin-dialog";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebLinksAddon } from "@xterm/addon-web-links";
import { spawn, Pty } from "tauri-pty";

// Constants
const STORAGE_KEY = "rustfava_recent_files";
const MAX_RECENT = 5;

// Types
interface TabInfo {
  tab_id: string;
  url: string;
  path: string;
  name: string;
}

interface OpenFileResult {
  tab_id: string;
  url: string;
  path: string;
  already_open: boolean;
}

// Terminal instance type
interface TerminalInstance {
  id: string;
  name: string;
  terminal: Terminal;
  fitAddon: FitAddon;
  pty: Pty | null;
  element: HTMLDivElement;
}

// State
let tabs: TabInfo[] = [];
let activeTabId: string | null = null;
let terminals: TerminalInstance[] = [];
let activeTerminalId: string | null = null;
let terminalVisible = false;
let terminalHeight = 300;
let terminalIdCounter = 0;

// Elements
const tabsEl = document.getElementById("tabs")!;
const tabContentsEl = document.getElementById("tabContents")!;
const welcomeEl = document.getElementById("welcome")!;
const loadingEl = document.getElementById("loadingOverlay")!;
const openBtn = document.getElementById("openBtn")!;
const openExampleBtn = document.getElementById("openExampleBtn")!;
const newTabBtn = document.getElementById("newTabBtn")!;
const terminalPanel = document.getElementById("terminalPanel")!;
const terminalBody = document.getElementById("terminalBody")!;
const terminalToggle = document.getElementById("terminalToggle")!;
const terminalClose = document.getElementById("terminalClose")!;
const terminalClear = document.getElementById("terminalClear")!;
const terminalNew = document.getElementById("terminalNew")!;
const terminalList = document.getElementById("terminalList")!;
const terminalResizeHandle = document.getElementById("terminalResizeHandle")!;
const contentEl = document.getElementById("content")!;
const footerBar = document.getElementById("footerBar")!;
const footerPath = document.getElementById("footerPath")!;

// Terminal theme matching rustfava colors
const terminalTheme = {
  background: "#0c1222",
  foreground: "#e2e8f0",
  cursor: "#f97316",
  cursorAccent: "#0c1222",
  selectionBackground: "rgba(249, 115, 22, 0.3)",
  selectionForeground: "#ffffff",
  black: "#1e293b",
  red: "#ef4444",
  green: "#22c55e",
  yellow: "#f59e0b",
  blue: "#3b82f6",
  magenta: "#a855f7",
  cyan: "#06b6d4",
  white: "#f1f5f9",
  brightBlack: "#475569",
  brightRed: "#f87171",
  brightGreen: "#4ade80",
  brightYellow: "#fbbf24",
  brightBlue: "#60a5fa",
  brightMagenta: "#c084fc",
  brightCyan: "#22d3ee",
  brightWhite: "#ffffff",
};

// Recent files
function getRecentFiles(): string[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function addRecentFile(path: string) {
  let recent = getRecentFiles().filter((p) => p !== path);
  recent.unshift(path);
  recent = recent.slice(0, MAX_RECENT);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(recent));
  renderRecentFiles();
}

function renderRecentFiles() {
  const recent = getRecentFiles();
  const sidebar = document.getElementById("sidebar")!;
  const list = document.getElementById("recentList")!;

  if (recent.length === 0) {
    sidebar.classList.add("empty");
    return;
  }

  sidebar.classList.remove("empty");
  list.innerHTML = recent
    .map((path) => {
      const name = path.split("/").pop();
      const dir = path.split("/").slice(0, -1).join("/");
      const shortDir = dir.length > 40 ? "..." + dir.slice(-37) : dir;
      return `
      <li class="recent-item" data-path="${path}">
        <div class="file-icon">&#128196;</div>
        <div class="name" title="${name}">${name}</div>
        <div class="path" title="${dir}">${shortDir}</div>
      </li>
    `;
    })
    .join("");

  list.querySelectorAll(".recent-item").forEach((item) => {
    item.addEventListener("click", () => {
      const path = (item as HTMLElement).dataset.path!;
      openPath(path);
    });
  });
}

// Tab management
function renderTabs() {
  tabsEl.innerHTML = tabs
    .map(
      (tab) => `
    <div class="tab ${tab.tab_id === activeTabId ? "active" : ""}" data-id="${tab.tab_id}">
      <span class="tab-name" title="${tab.path}">${tab.name}</span>
      <span class="tab-close" data-id="${tab.tab_id}">&times;</span>
    </div>
  `
    )
    .join("");

  // Tab click handlers
  tabsEl.querySelectorAll(".tab").forEach((el) => {
    el.addEventListener("click", (e) => {
      if (!(e.target as HTMLElement).classList.contains("tab-close")) {
        switchTab((el as HTMLElement).dataset.id!);
      }
    });
  });

  // Close button handlers
  tabsEl.querySelectorAll(".tab-close").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      closeTab((el as HTMLElement).dataset.id!);
    });
  });

  // Show/hide welcome screen and footer bar
  if (tabs.length === 0) {
    welcomeEl.classList.remove("hidden");
    footerBar.classList.remove("visible");
    hideTerminal();
  } else {
    welcomeEl.classList.add("hidden");
    footerBar.classList.add("visible");

    // Update footer path with active tab
    const activeTab = tabs.find((t) => t.tab_id === activeTabId);
    if (activeTab) {
      footerPath.textContent = activeTab.path;
    }
  }
}

function renderTabContents() {
  const existingIds = new Set(
    [...tabContentsEl.querySelectorAll(".tab-content")].map(
      (el) => (el as HTMLElement).dataset.id
    )
  );

  tabs.forEach((tab) => {
    if (!existingIds.has(tab.tab_id)) {
      const div = document.createElement("div");
      div.className = "tab-content";
      div.dataset.id = tab.tab_id;
      div.innerHTML = `<iframe src="${tab.url}"></iframe>`;
      tabContentsEl.appendChild(div);
    }
  });

  // Remove iframes for closed tabs
  tabContentsEl.querySelectorAll(".tab-content").forEach((el) => {
    if (!tabs.find((t) => t.tab_id === (el as HTMLElement).dataset.id)) {
      el.remove();
    }
  });

  // Show active tab
  tabContentsEl.querySelectorAll(".tab-content").forEach((el) => {
    el.classList.toggle(
      "active",
      (el as HTMLElement).dataset.id === activeTabId
    );
  });
}

function switchTab(tabId: string) {
  activeTabId = tabId;
  renderTabs();
  renderTabContents();
}

async function closeTab(tabId: string) {
  try {
    await invoke("close_tab", { tabId });

    const idx = tabs.findIndex((t) => t.tab_id === tabId);
    tabs = tabs.filter((t) => t.tab_id !== tabId);

    // Kill all terminals if closing last tab
    if (tabs.length === 0) {
      terminals.forEach((t) => {
        if (t.pty) t.pty.kill();
        t.element.remove();
      });
      terminals.length = 0;
      activeTerminalId = null;
    }

    // Switch to another tab if closing active
    if (activeTabId === tabId) {
      if (tabs.length > 0) {
        activeTabId = tabs[Math.max(0, idx - 1)].tab_id;
      } else {
        activeTabId = null;
      }
    }

    renderTabs();
    renderTabContents();
  } catch (err) {
    console.error("Failed to close tab:", err);
  }
}

// Open file
async function openPath(path: string) {
  loadingEl.classList.remove("hidden");

  try {
    const result = await invoke<OpenFileResult>("open_file", { path });

    addRecentFile(path);

    if (result.already_open) {
      switchTab(result.tab_id);
      loadingEl.classList.add("hidden");
      return;
    }

    // Wait for server to be ready
    await waitForServer(result.url);

    // Add new tab
    tabs.push({
      tab_id: result.tab_id,
      url: result.url,
      path: result.path,
      name: result.path.split("/").pop() || result.path,
    });
    activeTabId = result.tab_id;

    renderTabs();
    renderTabContents();

    // Auto-open terminal after loading a file
    setTimeout(() => {
      showTerminal();
    }, 500);
  } catch (err) {
    console.error("Failed to open file:", err);
    alert("Failed to open file: " + err);
  } finally {
    loadingEl.classList.add("hidden");
  }
}

async function waitForServer(url: string, maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      await fetch(url, { mode: "no-cors" });
      return;
    } catch {
      await new Promise((r) => setTimeout(r, 200));
    }
  }
  throw new Error("Server failed to start");
}

async function openFilePicker() {
  try {
    const path = await open({
      multiple: false,
      filters: [
        {
          name: "Beancount",
          extensions: ["beancount", "bean"],
        },
      ],
    });

    if (path) {
      await openPath(path as string);
    }
  } catch (err) {
    console.error("File picker error:", err);
  }
}

// Terminal functions
interface ShellInfo {
  shell: string;
  args: string[];
}

function getShellName(shellPath: string): string {
  return shellPath.split("/").pop() || "terminal";
}

function createTerminalInstance(cwd: string): TerminalInstance {
  const id = `term_${++terminalIdCounter}`;

  // Create container element
  const element = document.createElement("div");
  element.className = "terminal-container";
  element.dataset.id = id;
  terminalBody.appendChild(element);

  // Create xterm instance
  const terminal = new Terminal({
    theme: terminalTheme,
    fontFamily:
      "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Menlo, Monaco, 'Courier New', monospace",
    fontSize: 13,
    lineHeight: 1.4,
    cursorBlink: true,
    cursorStyle: "bar",
    scrollback: 10000,
    allowProposedApi: true,
  });

  const fitAddon = new FitAddon();
  const webLinksAddon = new WebLinksAddon();

  terminal.loadAddon(fitAddon);
  terminal.loadAddon(webLinksAddon);
  terminal.open(element);

  const instance: TerminalInstance = {
    id,
    name: `Terminal ${terminalIdCounter}`,
    terminal,
    fitAddon,
    pty: null,
    element,
  };

  return instance;
}

type TerminalEnv = Record<string, string>;

async function spawnPtyForTerminal(instance: TerminalInstance, cwd: string) {
  // Get the directory from the file path
  const dir = cwd.split("/").slice(0, -1).join("/") || cwd;

  // Get user's default shell and terminal environment from Rust backend
  const [shellInfo, terminalEnv] = await Promise.all([
    invoke<ShellInfo>("get_default_shell"),
    invoke<TerminalEnv>("get_terminal_env").catch(() => null),
  ]);

  // Update terminal name based on shell
  instance.name = getShellName(shellInfo.shell);
  renderTerminalList();

  try {
    // Start user's default shell with sidecar binaries in PATH
    instance.pty = spawn(shellInfo.shell, shellInfo.args, {
      cols: instance.terminal.cols,
      rows: instance.terminal.rows,
      cwd: dir,
      ...(terminalEnv ? { env: terminalEnv } : {}),
    });

    // Show welcome message with available commands
    instance.terminal.write("\r\n");
    instance.terminal.write("  \x1b[1m\x1b[38;5;208mrustfava terminal\x1b[0m\r\n");
    instance.terminal.write("  \x1b[38;5;245m─────────────────\x1b[0m\r\n");
    instance.terminal.write("\r\n");
    instance.terminal.write("  \x1b[36mrledger-check\x1b[0m   \x1b[38;5;245m(bean-check)\x1b[0m   - Validate beancount files\r\n");
    instance.terminal.write("  \x1b[36mrledger-query\x1b[0m   \x1b[38;5;245m(bean-query)\x1b[0m   - Query ledger with BQL\r\n");
    instance.terminal.write("  \x1b[36mrledger-format\x1b[0m  \x1b[38;5;245m(bean-format)\x1b[0m  - Format beancount files\r\n");
    instance.terminal.write("  \x1b[36mrledger-doctor\x1b[0m  \x1b[38;5;245m(bean-doctor)\x1b[0m  - Diagnose issues in ledger\r\n");
    instance.terminal.write("  \x1b[36mrledger-report\x1b[0m  \x1b[38;5;245m(bean-report)\x1b[0m  - Generate reports\r\n");
    instance.terminal.write("  \x1b[36mrledger-price\x1b[0m   \x1b[38;5;245m(bean-price)\x1b[0m   - Fetch price quotes\r\n");
    instance.terminal.write("  \x1b[36mrledger-extract\x1b[0m \x1b[38;5;245m(bean-extract)\x1b[0m - Extract transactions\r\n");
    instance.terminal.write("\r\n");
    instance.terminal.write("  \x1b[38;5;245mRun any command with --help for usage info\x1b[0m\r\n");
    instance.terminal.write("\r\n");

    // Run rledger-check on the current file after a short delay
    setTimeout(() => {
      if (instance.pty) {
        const filePath = cwd; // cwd is the file path passed to spawnPtyForTerminal
        instance.pty.write(`rledger-check "${filePath}"\n`);
      }
    }, 500);

    // Handle PTY output
    const decoder = new TextDecoder();
    instance.pty.onData((data: Uint8Array | string) => {
      let text: string;
      if (typeof data === "string") {
        text = data;
      } else if (data instanceof Uint8Array) {
        text = decoder.decode(data);
      } else {
        text = decoder.decode(new Uint8Array(data as any));
      }
      instance.terminal.write(text);
    });

    instance.pty.onExit(({ exitCode }) => {
      instance.terminal.write(`\r\n\x1b[90m[Process exited with code ${exitCode}]\x1b[0m\r\n`);
      instance.pty = null;
      instance.name = `${instance.name} (exited)`;
      renderTerminalList();
    });

    // Set up input handler
    instance.terminal.onData((data: string) => {
      if (instance.pty) {
        instance.pty.write(data);
      }
    });

    // Handle terminal resize
    instance.terminal.onResize(({ cols, rows }) => {
      if (instance.pty) {
        instance.pty.resize(cols, rows);
      }
    });
  } catch (err) {
    console.error("Failed to spawn terminal:", err);
    instance.terminal.write(`\x1b[31mFailed to spawn terminal: ${err}\x1b[0m\r\n`);
  }
}

function renderTerminalList() {
  terminalList.innerHTML = terminals
    .map(
      (t) => `
    <div class="terminal-list-item ${t.id === activeTerminalId ? "active" : ""}" data-id="${t.id}">
      <span class="terminal-icon">&#9654;</span>
      <span class="terminal-name" data-id="${t.id}">${t.name}</span>
      <span class="terminal-close" data-id="${t.id}">&times;</span>
    </div>
  `
    )
    .join("");

  // Add click handlers
  terminalList.querySelectorAll(".terminal-list-item").forEach((el) => {
    el.addEventListener("click", (e) => {
      if (!(e.target as HTMLElement).classList.contains("terminal-close") &&
          !(e.target as HTMLElement).classList.contains("terminal-name-input")) {
        switchTerminal((el as HTMLElement).dataset.id!);
      }
    });
  });

  // Add double-click to rename
  terminalList.querySelectorAll(".terminal-name").forEach((el) => {
    el.addEventListener("dblclick", (e) => {
      e.stopPropagation();
      const id = (el as HTMLElement).dataset.id!;
      startRenameTerminal(id, el as HTMLElement);
    });
  });

  // Add close handlers
  terminalList.querySelectorAll(".terminal-close").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      closeTerminal((el as HTMLElement).dataset.id!);
    });
  });
}

function startRenameTerminal(id: string, nameEl: HTMLElement) {
  const instance = terminals.find((t) => t.id === id);
  if (!instance) return;

  const input = document.createElement("input");
  input.type = "text";
  input.className = "terminal-name-input";
  input.value = instance.name;
  input.dataset.id = id;

  // Replace span with input
  nameEl.replaceWith(input);
  input.focus();
  input.select();

  const finishRename = () => {
    const newName = input.value.trim() || instance.name;
    instance.name = newName;
    renderTerminalList();
  };

  input.addEventListener("blur", finishRename);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      input.blur();
    } else if (e.key === "Escape") {
      e.preventDefault();
      renderTerminalList(); // Cancel - re-render without saving
    }
  });
}

function switchTerminal(id: string) {
  activeTerminalId = id;

  // Update active states
  terminals.forEach((t) => {
    t.element.classList.toggle("active", t.id === id);
  });

  // Focus and fit the active terminal
  const active = terminals.find((t) => t.id === id);
  if (active) {
    setTimeout(() => {
      active.fitAddon.fit();
      active.terminal.focus();
    }, 50);
  }

  renderTerminalList();
}

function closeTerminal(id: string) {
  const idx = terminals.findIndex((t) => t.id === id);
  if (idx === -1) return;

  const instance = terminals[idx];

  // Kill PTY
  if (instance.pty) {
    instance.pty.kill();
  }

  // Remove element
  instance.element.remove();

  // Remove from array
  terminals.splice(idx, 1);

  // Switch to another terminal or hide panel
  if (terminals.length === 0) {
    activeTerminalId = null;
    hideTerminal();
  } else if (activeTerminalId === id) {
    activeTerminalId = terminals[Math.max(0, idx - 1)].id;
    switchTerminal(activeTerminalId);
  }

  renderTerminalList();
}

async function createNewTerminal() {
  if (!activeTabId) return;

  const tab = tabs.find((t) => t.tab_id === activeTabId);
  if (!tab) return;

  const instance = createTerminalInstance(tab.path);
  terminals.push(instance);
  activeTerminalId = instance.id;

  renderTerminalList();
  switchTerminal(instance.id);

  // Fit after DOM update
  setTimeout(() => {
    instance.fitAddon.fit();
  }, 50);

  // Spawn PTY
  await spawnPtyForTerminal(instance, tab.path);
}

function showTerminal() {
  terminalPanel.classList.add("visible");
  contentEl.classList.add("terminal-open");
  terminalVisible = true;
  terminalToggle.classList.add("active");

  // Create first terminal if none exist
  if (terminals.length === 0 && activeTabId) {
    createNewTerminal();
  } else if (activeTerminalId) {
    // Fit and focus existing terminal
    setTimeout(() => {
      const active = terminals.find((t) => t.id === activeTerminalId);
      if (active) {
        active.fitAddon.fit();
        active.terminal.focus();
      }
    }, 300);
  }
}

function hideTerminal() {
  terminalPanel.classList.remove("visible");
  contentEl.classList.remove("terminal-open");
  terminalVisible = false;
  terminalToggle.classList.remove("active");
}

function toggleTerminal() {
  if (terminalVisible) {
    hideTerminal();
  } else {
    showTerminal();
  }
}

function fitAllTerminals() {
  terminals.forEach((t) => {
    if (t.element.classList.contains("active")) {
      t.fitAddon.fit();
    }
  });
}

// Terminal resize handling
let isResizing = false;
let startY = 0;
let startHeight = 0;

terminalResizeHandle.addEventListener("mousedown", (e) => {
  isResizing = true;
  startY = e.clientY;
  startHeight = terminalHeight;
  document.body.style.cursor = "ns-resize";
  document.body.style.userSelect = "none";
  // Disable pointer events on iframes during resize to prevent mouse capture
  document.querySelectorAll("iframe").forEach((iframe) => {
    (iframe as HTMLIFrameElement).style.pointerEvents = "none";
  });
});

document.addEventListener("mousemove", (e) => {
  if (!isResizing) return;

  const delta = startY - e.clientY;
  terminalHeight = Math.max(
    150,
    Math.min(window.innerHeight - 100, startHeight + delta)
  );
  terminalPanel.style.height = terminalHeight + "px";

  // Update tab content bottom offset
  const tabContents = document.querySelectorAll(".tab-content");
  tabContents.forEach((el) => {
    if (terminalVisible) {
      (el as HTMLElement).style.bottom = terminalHeight + "px";
    }
  });

  fitAllTerminals();
});

document.addEventListener("mouseup", () => {
  if (isResizing) {
    isResizing = false;
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
    // Re-enable pointer events on iframes
    document.querySelectorAll("iframe").forEach((iframe) => {
      (iframe as HTMLIFrameElement).style.pointerEvents = "";
    });
  }
});

// Open the bundled example file
async function openExampleFile() {
  try {
    const path = await invoke<string>("get_example_file_path");
    await openPath(path);
  } catch (err) {
    console.error("Failed to open example file:", err);
    alert("Failed to open example file: " + err);
  }
}

// Event listeners
openBtn.addEventListener("click", openFilePicker);
openExampleBtn.addEventListener("click", openExampleFile);
newTabBtn.addEventListener("click", openFilePicker);
terminalToggle.addEventListener("click", toggleTerminal);
terminalClose.addEventListener("click", hideTerminal);
terminalNew.addEventListener("click", createNewTerminal);
terminalClear.addEventListener("click", () => {
  const active = terminals.find((t) => t.id === activeTerminalId);
  if (active) active.terminal.clear();
});

// Menu events from Rust
listen("menu-open-file", () => openFilePicker());
listen("menu-close-tab", () => {
  if (activeTabId) closeTab(activeTabId);
});
listen("menu-reload", () => {
  const iframe = tabContentsEl.querySelector(
    `.tab-content[data-id="${activeTabId}"] iframe`
  ) as HTMLIFrameElement;
  if (iframe) iframe.src = iframe.src;
});
listen("menu-toggle-terminal", () => {
  if (tabs.length > 0) {
    toggleTerminal();
  }
});

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "o") {
    e.preventDefault();
    openFilePicker();
  }
  if ((e.ctrlKey || e.metaKey) && e.key === "w") {
    e.preventDefault();
    if (activeTabId) closeTab(activeTabId);
  }
  if ((e.ctrlKey || e.metaKey) && e.key === "`") {
    e.preventDefault();
    if (tabs.length > 0) {
      toggleTerminal();
    }
  }
});

// Resize terminal on window resize
window.addEventListener("resize", () => {
  if (terminalVisible) {
    fitAllTerminals();
  }
});

// Initialize
renderRecentFiles();
renderTabs();
