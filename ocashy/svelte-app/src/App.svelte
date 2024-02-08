<script>
    import { onMount } from 'svelte';
    import Routes from './pages/routes.svelte';
    let online = false;

    async function getMessage() {
        try {
            const response = await fetch('http://localhost:8000');
            const data = await response.json();
            online = data.Hello === "World";
        } catch (error) {
            console.error('Fetch error:', error);
            online = false;
        }
    }

    onMount(() => {
        getMessage();
    });
</script>

<div class="navbar">
    <p style="color : #fff">[Your-Company-Name] | Ocashy app Beta 0.1 | Status: 
        {#if online}
            <b style="color: #85ffa7;">Online</b>
        {:else}
            <b style="color: #ff8b85;">Offline</b>
        {/if}
    </p>
</div>

<div class="app-container">
    <div class="sidebar">
        <h2>Menu</h2>
        <ul>
            <a href="#categories"><li><span class="icon">📁</span>Daftar Produk</li></a>
            <a href="#files"><li><span class="icon">📄</span>Daftar Nota</li></a>
            <a href="#cashier"><li><span class="icon">🖊️</span>Buat Nota</li></a>
            <a href="#edit"><li><span class="icon">🔣</span>Edit Produk</li></a>
            <a href="{window.location.href}" target="_blank"><li><span class="icon">➕</span>New Page</li></a>
            <a href="#help"><li><span class="icon">❓</span>Help</li></a>
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
        background: #036ac4;
        padding: 0 20px;
        z-index: 1000;
        box-sizing: border-box;
        position: fixed;
        top: 0;
        left: 0;
    }

    .sidebar {
        width: 250px; /* Adjusted to match the design */
        background-color: #ffffff;
        padding: 20px;
        height: 100vh;
        box-sizing: border-box;
        position: fixed;
        top: 60px; /* Height of the navbar */
    }

    .sidebar ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .sidebar li {
        display: flex;
        align-items: center;
        margin: 10px 0;
        padding: 10px 20px;
    }

    .sidebar li:hover {
        background-color: #d8e9f8; /* Slightly darker background on hover */
        border-radius: 4px;
    }

    .sidebar .icon {
        margin-right: 10px;
    }

    .sidebar a {
        text-decoration: none;
        color: #333;
        font-weight: bold;
        display: block;
        flex-grow: 1;
    }

    .main-content {
        flex-grow: 1;
        margin-left: 250px; /* Same as sidebar width */
        margin-top: 60px; /* Same as navbar height */
        padding: 20px;
    }
</style>
