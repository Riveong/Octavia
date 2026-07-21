<script>
    import { onMount } from 'svelte';

    let fallbackEnabled = true;
    let silentPrintEnabled = true;
    let migrating = false;

    let newDbSettings = {
        host: '',
        dbase: '',
        duser: '',
        dpw: ''
    };

    onMount(() => {
        // Load settings from localStorage, default to true if not set
        const storedFallback = localStorage.getItem('fallbackEnabled');
        const storedSilent = localStorage.getItem('silentPrintEnabled');

        if (storedFallback !== null) {
            fallbackEnabled = storedFallback === 'true';
        } else {
            localStorage.setItem('fallbackEnabled', 'true');
        }

        if (storedSilent !== null) {
            silentPrintEnabled = storedSilent === 'true';
        } else {
            localStorage.setItem('silentPrintEnabled', 'true');
        }
    });

    function saveSettings() {
        localStorage.setItem('fallbackEnabled', fallbackEnabled.toString());
        localStorage.setItem('silentPrintEnabled', silentPrintEnabled.toString());
    }

    function downloadBackup() {
        window.open('http://localhost:8000/backup-db', '_blank');
    }

    async function migrateDatabase() {
        if (!newDbSettings.host.trim() || !newDbSettings.dbase.trim() || !newDbSettings.duser.trim()) {
            alert('Mohon isi Host, Nama Database, dan User!');
            return;
        }

        const confirmMigration = confirm(`Apakah Anda yakin ingin memindahkan data ke database "${newDbSettings.dbase}"? Ini juga akan mengubah file .env.`);
        if (!confirmMigration) return;

        migrating = true;
        try {
            const response = await fetch('http://localhost:8000/migrate-db', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newDbSettings)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Gagal melakukan migrasi database.');
            }

            const data = await response.json();
            alert(data.message);
            newDbSettings = { host: '', dbase: '', duser: '', dpw: '' };
        } catch (error) {
            console.error('Migration error:', error);
            alert(`Error: ${error.message}`);
        } finally {
            migrating = false;
        }
    }
</script>

<h1>Settings</h1>
<p>Configure your Ocashy cashier application preferences here.</p>

<div class="settings-group">
    <h3>General Settings</h3>
    <label>
        <input type="checkbox" bind:checked={fallbackEnabled} on:change={saveSettings} />
        Enable Fallback Offline Mode (SQLite)
    </label>
    <br/>
    <label>
        <input type="checkbox" bind:checked={silentPrintEnabled} on:change={saveSettings} />
        Silent Printing via SumatraPDF
    </label>
</div>

<div class="settings-group" style="margin-top: 20px;">
    <h3>Printer Configuration</h3>
    <p>Printing properties configured: A4 (210 x 297 mm), Scale: Actual size (noscale), Orientation: Landscape.</p>
</div>

<div class="settings-group" style="margin-top: 20px;">
    <h3>Database Backup</h3>
    <p>Export the current inventory database to a standard SQL file.</p>
    <button on:click={downloadBackup} class="btn-backup">Backup Database (.sql)</button>
</div>

<div class="settings-group" style="margin-top: 20px;">
    <h3>Migrate Database</h3>
    <p>Clone the active inventory data to a new MySQL database and update connection settings.</p>
    
    <div class="form-grid-two">
        <div class="form-group">
            <label for="new_host">Database Host (IP/Host)</label>
            <input id="new_host" type="text" placeholder="localhost" bind:value={newDbSettings.host} />
        </div>
        <div class="form-group">
            <label for="new_dbase">Database Name</label>
            <input id="new_dbase" type="text" placeholder="ocashy_new" bind:value={newDbSettings.dbase} />
        </div>
    </div>
    <div class="form-grid-two" style="margin-top: 10px;">
        <div class="form-group">
            <label for="new_duser">Database User</label>
            <input id="new_duser" type="text" placeholder="root" bind:value={newDbSettings.duser} />
        </div>
        <div class="form-group">
            <label for="new_dpw">Database Password</label>
            <input id="new_dpw" type="password" placeholder="Password" bind:value={newDbSettings.dpw} />
        </div>
    </div>
    
    <button on:click={migrateDatabase} class="btn-migrate" disabled={migrating}>
        {#if migrating}
            Migrating...
        {:else}
            Migrate & Update .env
        {/if}
    </button>
</div>

<style>
    .settings-group {
        background: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    label {
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
        cursor: pointer;
    }
    .btn-backup {
        background-color: #6c757d;
        color: white;
        font-weight: bold;
        cursor: pointer;
        padding: 10px 15px;
        border: none;
        border-radius: 4px;
        margin-top: 10px;
    }
    .btn-backup:hover {
        background-color: #5a6268;
    }
    .form-grid-two {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 10px;
    }
    .form-group {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .form-group label {
        font-size: 13px;
        font-weight: 600;
        color: #495057;
        margin-top: 0;
    }
    .form-group input {
        padding: 10px 14px;
        border: 1px solid #ced4da;
        border-radius: 6px;
        font-size: 14px;
        color: #212529;
        outline: none;
        transition: all 0.15s ease-in-out;
    }
    .form-group input:focus {
        border-color: #036ac4;
        box-shadow: 0 0 0 3px rgba(3, 106, 196, 0.12);
    }
    .btn-migrate {
        background-color: #f08c00;
        color: white;
        font-weight: bold;
        cursor: pointer;
        padding: 10px 15px;
        border: none;
        border-radius: 4px;
        margin-top: 15px;
        transition: background-color 0.2s;
    }
    .btn-migrate:hover:not(:disabled) {
        background-color: #e67700;
    }
    .btn-migrate:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
</style>
