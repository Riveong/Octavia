<script>
    import { onMount, onDestroy } from 'svelte';
    import Routes from './pages/routes.svelte';
    let dbStatus = "offline"; // "online", "offline_mode", "offline"
    let currentRoute = '';

    function hashChange() {
        currentRoute = window.location.hash || '#categories';
    }

    async function getMessage() {
        try {
            const response = await fetch('http://localhost:8000');
            const data = await response.json();
            if (data.Hello === "World") {
                if (data.database === "sqlite") {
                    dbStatus = "offline_mode";
                } else {
                    dbStatus = "online";
                }
            } else {
                dbStatus = "offline";
            }
        } catch (error) {
            console.error('Fetch error:', error);
            dbStatus = "offline";
        }
    }

    async function spawnNewPage() {
        if (typeof Neutralino === 'undefined') {
            window.open(window.location.href, '_blank');
            return;
        }

        try {
            let binaryName = 'neutralino-win_x64.exe';
            if (NL_OS === 'Darwin') {
                binaryName = NL_PATH.includes('dist') ? 'neu-mac_x64' : 'neutralino-mac_x64';
            } else if (NL_OS === 'Linux') {
                binaryName = NL_PATH.includes('dist') ? 'neu-linux_x64' : 'neutralino-linux_x64';
            } else {
                binaryName = NL_PATH.includes('dist') ? 'neu-win_x64.exe' : 'neutralino-win_x64.exe';
            }
            await Neutralino.os.spawnProcess(`${NL_PATH}/${binaryName}`);
        } catch (e) {
            console.error("Failed to spawn new page:", e);
            window.open(window.location.href, '_blank');
        }
    }

    onMount(() => {
        getMessage();
        window.addEventListener('hashchange', hashChange);
        hashChange();
    });

    onDestroy(() => {
        window.removeEventListener('hashchange', hashChange);
    });
</script>

<div class="navbar">
    <div class="navbar-brand">
        <span class="brand-logo">🏪</span>
        <span class="brand-name">Istana Keramik</span>
        <span class="brand-divider">|</span>
        <span class="brand-version">Ocashy App v1</span>
    </div>
    <div class="navbar-status">
        <span class="status-label">Status:</span>
        {#if dbStatus === 'online'}
            <span class="badge badge-online">
                <span class="badge-dot"></span>
                Online
            </span>
        {:else if dbStatus === 'offline_mode'}
            <span class="badge badge-offline-mode">
                <span class="badge-dot"></span>
                Offline Mode
            </span>
        {:else}
            <span class="badge badge-offline">
                <span class="badge-dot"></span>
                Offline
            </span>
        {/if}
    </div>
</div>

<div class="app-container">
    <div class="sidebar">
        <h2 class="sidebar-title">Menu</h2>
        <ul>
            <a href="#categories" class:active={currentRoute === '#categories'}><li><span class="icon">📁</span>Daftar Produk</li></a>
            <a href="#files" class:active={currentRoute === '#files'}><li><span class="icon">📄</span>Daftar Nota</li></a>
            <a href="#cashier" class:active={currentRoute === '#cashier'}><li><span class="icon">🖊️</span>Buat Nota</li></a>
            <a href="#add" class:active={currentRoute === '#add'}><li><span class="icon">🆕</span>Tambah Produk</li></a>
            <a href="#edit" class:active={currentRoute === '#edit'}><li><span class="icon">🔣</span>Edit Produk</li></a>
            <a href="#new-page" on:click|preventDefault={spawnNewPage}><li><span class="icon">➕</span>New Page</li></a>
            <a href="#settings" class:active={currentRoute === '#settings'}><li><span class="icon">⚙️</span>Settings</li></a>
            <a href="#help" class:active={currentRoute === '#help'}><li><span class="icon">❓</span>Help</li></a>
        </ul>
    </div>

    <div class="main-content">
        <Routes />

    </div>
</div>

<style>
    .app-container {
        display: flex;
    }

    .navbar {
        width: 100%;
        background: #ffffff;
        color: #333333;
        border-bottom: 1px solid #e9ecef;
        padding: 12px 24px;
        z-index: 1000;
        box-sizing: border-box;
        position: fixed;
        top: 0;
        left: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 60px;
    }

    .navbar-brand {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .brand-logo {
        font-size: 20px;
    }

    .brand-name {
        font-weight: 700;
        color: #212529;
        font-size: 16px;
        letter-spacing: -0.2px;
    }

    .brand-divider {
        color: #dee2e6;
        margin: 0 4px;
    }

    .brand-version {
        color: #868e96;
        font-size: 13px;
        font-weight: 500;
    }

    .navbar-status {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .status-label {
        font-size: 13px;
        font-weight: 500;
        color: #868e96;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.2px;
    }

    .badge-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }

    .badge-online {
        background-color: #e6fcf5;
        color: #0ca678;
        border: 1px solid #c3fae8;
    }
    .badge-online .badge-dot {
        background-color: #0ca678;
    }

    .badge-offline-mode {
        background-color: #fff9db;
        color: #f08c00;
        border: 1px solid #fff3bf;
    }
    .badge-offline-mode .badge-dot {
        background-color: #f08c00;
    }

    .badge-offline {
        background-color: #fff5f5;
        color: #f03e3e;
        border: 1px solid #ffe3e3;
    }
    .badge-offline .badge-dot {
        background-color: #f03e3e;
    }

    .sidebar {
        width: 250px;
        background-color: #202124; /* Premium Dark Gray */
        padding: 20px 15px;
        height: 100vh;
        box-sizing: border-box;
        position: fixed;
        top: 60px; /* Height of the navbar */
        border-right: 1px solid #3c4043;
    }

    .sidebar-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #80868b;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 15px;
        padding-left: 15px;
    }

    .sidebar ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .sidebar a {
        text-decoration: none;
        color: #bdc1c6;
        font-size: 14px;
        font-weight: 500;
        display: block;
        margin-bottom: 4px;
        border-radius: 6px;
        transition: all 0.2s ease-in-out;
    }

    .sidebar a li {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        margin: 0;
        list-style: none;
    }

    .sidebar a:hover {
        background-color: #303134;
        color: #ffffff;
    }

    .sidebar a.active {
        background-color: #303134;
        color: #ffffff;
        font-weight: 600;
        text-decoration: underline;
        text-underline-offset: 4px;
    }

    .sidebar .icon {
        margin-right: 12px;
        font-size: 16px;
        display: inline-block;
        transition: transform 0.2s;
    }

    .sidebar a:hover .icon {
        transform: scale(1.1);
    }

    .main-content {
        flex-grow: 1;
        margin-left: 250px; /* Same as sidebar width */
        margin-top: 60px; /* Same as navbar height */
        padding: 20px;
    }
</style>
