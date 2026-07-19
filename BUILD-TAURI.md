# Building the Tauri Desktop Version

This guide outlines the system prerequisites, environment fixes, and compilation steps required to build the Tauri version of the application. 

---

## Agent Instruction Prompt (Action Plan)
If you are an AI agent, you must execute these steps to ensure a successful compilation:

1. **Detect / Fix Linker Shadowing:** Check if `C:\Program Files\Git\usr\bin\link.exe` exists. If yes, rename it to `link.exe.bak` to prevent it from shadowing MSVC's linker.
2. **Install C++ Build Tools:** Check if Visual Studio Build Tools with C++ workload is installed. If not, trigger an elevated `winget` installation.
3. **Install SumatraPDF:** Check if SumatraPDF is installed. If not, run the winget install command.
4. **Verify Rust & Target:** Ensure the Rust toolchain `stable-x86_64-pc-windows-msvc` is installed.
5. **Build Frontend:** Run `npm install` and `npm run build` in the Tauri folder.
6. **Compile Tauri:** Run the Tauri build command.

---

## Setup & Build Commands (Administrator PowerShell)

Run the following commands in an **Administrator PowerShell** window:

### Step 1: Fix Git link.exe Conflict
```powershell
# Rename Git's GNU link utility to prevent it from intercepting MSVC linker arguments
Rename-Item -Path "C:\Program Files\Git\usr\bin\link.exe" -NewName "link.exe.bak" -Force -ErrorAction SilentlyContinue
```

### Step 2: Install Microsoft C++ Build Tools (Requires Reboot)
```powershell
# Download and install C++ Build Tools & Windows SDK silently
winget install --id Microsoft.VisualStudio.2022.BuildTools --override "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --passive"
```
*(Note: Please **restart your PC** after the winget command finishes to update system environment variables).*

### Step 3: Install SumatraPDF (For Silent Printing)
```powershell
# Install SumatraPDF silently (required for silent receipt printing)
winget install -e --id SumatraPDF.SumatraPDF
```

### Step 4: Verify Rust MSVC Toolchain
```powershell
rustup target add x86_64-pc-windows-msvc
```

### Step 5: Run Tauri Build
Navigate to the Tauri project directory and build the installer package:
```powershell
# 1. Go to desktop directory
cd "ocashy-desktop"

# 2. Install Svelte dependencies
npm install

# 3. Build and package the Tauri installer
npm run tauri build
```

### Build Output
The compiled MSI installer and standalone EXE will be generated in:
*   `ocashy-desktop/src-tauri/target/release/bundle/nsis/`
