<script>
    let pdfs = [];
    let filteredPdfs = [];
    let searchTerm = '';

    let loading = false;

    async function getPdfs() {
        loading = true;
        try {
            const response = await fetch('http://localhost:8000/pdfs');
            const data = await response.json();
            pdfs = data.pdf_files || [];
            filteredPdfs = pdfs;
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    function filterPdfs() {
        filteredPdfs = pdfs.filter((pdf) => {
            return pdf.toLowerCase().includes(searchTerm.toLowerCase());
        });
    }

    $: searchTerm, filterPdfs(); // Reactive statement to filter items when searchTerm changes

    getPdfs();
</script>

<h1>Daftar Nota</h1>

<input type="text" placeholder="Search..." bind:value={searchTerm} />

{#if loading}
    <div class="loading-container">
        <div class="spinner"></div>
        <p>Loading PDFs...</p>
    </div>
{:else}
<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {#each filteredPdfs as pdf (pdf)}
            <tr>
                <td>{pdf}</td>
                <td><a href={`http://localhost:8000/pdfs/${pdf}`} target="_blank">🔎</a></td>
            </tr>
        {/each}
    </tbody>
</table>
{/if}

<style>
    input[type="text"] {
        width: 100%;
        padding: 10px;
        margin-bottom: 20px;
        box-sizing: border-box;
    }
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
    }
    .spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #036ac4;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin-bottom: 10px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
