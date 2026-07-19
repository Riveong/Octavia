# Building the Neutralinojs Desktop Version (Single-File Binary)

This guide shows how to download Neutralino binaries, configure client libraries, and package the application into a single standalone `.exe` without compiling native C++/Rust.

---

## Agent Instruction Prompt (Action Plan)
If you are an AI agent, follow this sequence of tasks:

1. **Install SumatraPDF (Prerequisite):** If silent printing of receipts is required, verify SumatraPDF is installed. If not, trigger a `winget` installation.
2. **Navigate to Project:** Go to the `ocashy-neutralino` folder.
3. **Install Dependencies:** Run `npm install` (includes Vite, Svelte, and `@neutralinojs/neu` CLI).
4. **Download Neutralino Binaries:** Run `npm run neu:update` to download platform runtimes (v6.x) and client definitions.
5. **Compile Frontend:** Run `npm run build` (compiles Svelte app assets to `dist/`).
6. **Pack Standalone Binary:** Run `npm run neu:build` (bundles resources into the binary using the `--embed-resources` flag).

---

## Terminal Commands (PowerShell or Command Prompt)

Run the following commands in your shell:

```powershell
# 1. Install SumatraPDF silently (required for silent POS printing)
winget install -e --id SumatraPDF.SumatraPDF

# 2. Navigate to the Neutralino project directory
cd "ocashy-neutralino"

# 3. Install Svelte and Neutralino CLI dependencies
npm.cmd install

# 4. Download Neutralino runtime binaries and client scripts
npm.cmd run neu:update

# 5. Build the Svelte app assets (dist/)
npm.cmd run build

# 6. Pack assets into a single-file embedded binary
npm.cmd run neu:build
```

### Build Output
The self-contained, single-file executables will be located in:
*   `ocashy-neutralino/dist/ocashy/ocashy-win_x64.exe` (Windows)
*   `ocashy-neutralino/dist/ocashy/ocashy-mac_arm64` (macOS Apple Silicon)
*   `ocashy-neutralino/dist/ocashy/ocashy-linux_x64` (Linux)

---

## Dev Server & Live Editing (HMR)
To run the project in development mode with hot-reloading:
```powershell
npm.cmd run neu:run
```
*(This starts the Svelte Vite dev server at port `1420` and loads the Neutralino application shell linked to it).*
