import App from './App.svelte';

let backendProcessId = null;

async function checkAndStartBackend() {
	if (typeof Neutralino === 'undefined') return;

	// 1. Check if backend is already running
	let isRunning = false;
	try {
		const res = await fetch('http://localhost:8000/');
		if (res.ok || res.status) {
			isRunning = true;
		}
	} catch (err) {
		isRunning = false;
	}

	if (isRunning) {
		console.log("FastAPI backend is already running on port 8000.");
		return;
	}

	// 2. Start backend
	console.log("FastAPI backend is not running. Starting it...");
	
	// Determine paths. NL_PATH is the application folder root.
	// In dev: NL_PATH is 'ocashy/neu/bin' -> go up 2 levels to 'ocashy' -> 'ocashy/backend/api'
	// In prod: NL_PATH is 'ocashy/neu/dist/neu' -> go up 3 levels to 'ocashy' -> 'ocashy/backend/api'
	const isProd = NL_PATH.includes('dist');
	const backendCwd = isProd ? `${NL_PATH}/../../../backend/api` : `${NL_PATH}/../../backend/api`;

	const cmd = NL_OS === 'Windows' 
		? 'python -m uvicorn main:app --port 8000' 
		: 'uvicorn main:app --port 8000';

	try {
		const processInfo = await Neutralino.os.spawnProcess(cmd, {
			cwd: backendCwd
		});
		backendProcessId = processInfo.id;
		console.log("FastAPI backend started with process ID:", backendProcessId);
	} catch (e) {
		console.error("Failed to start FastAPI backend:", e);
	}
}

if (typeof Neutralino !== 'undefined') {
	Neutralino.init();
	checkAndStartBackend();

	Neutralino.events.on("windowClose", async () => {
		if (backendProcessId !== null) {
			console.log("Stopping FastAPI backend process...");
			try {
				await Neutralino.os.updateSpawnedProcess(backendProcessId, 'exit');
			} catch (e) {
				console.error("Error stopping backend process:", e);
			}
		}
		Neutralino.app.exit();
	});
}

const app = new App({
	target: document.body,
	props: {
		name: 'world'
	}
});

export default app;