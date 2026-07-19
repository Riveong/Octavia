# Building the Web Version (Static HTML/JS/CSS)

This guide is designed for developers or AI agents to compile the frontend codebase into a static web folder.

---

## Agent Instruction Prompt
If you are an AI agent, you can execute the following steps in sequence:

1. **Verify Node.js:** Check if Node.js is installed on the host system.
2. **Navigate to the Project:** Go to the web folder `ocashy-neutralino` (or `ocashy-desktop`).
3. **Install Dependencies:** Run `npm install`.
4. **Build Assets:** Run the Vite production build command.

---

## Terminal Execution Commands

Run these commands in PowerShell or Command Prompt:

```powershell
# 1. Navigate to the project folder
cd "ocashy-neutralino"

# 2. Install node modules
npm install

# 3. Build the static production bundle
npm run build
```

### Build Output
The compiled static assets will be located in:
*   `ocashy-neutralino/dist/`
