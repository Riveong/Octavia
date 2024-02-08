<script>
    let pdfs = [];
    let filteredPdfs = [];
    let searchTerm = '';

    async function getPdfs() {
        const response = await fetch('http://localhost:8000/pdfs');
        const data = await response.json();
        pdfs = data.pdf_files;
        filteredPdfs = pdfs;
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

<style>
    input[type="text"] {
        width: 100%;
        padding: 10px;
        margin-bottom: 20px;
        box-sizing: border-box;
    }
</style>
