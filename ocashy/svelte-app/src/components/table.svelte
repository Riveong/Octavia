<script>
    import { onMount } from "svelte";

    let items = [];
    let filteredItems = [];
    let page = 1;
    let maxPage;
    let searchQuery = '';

    let loading = false;

    async function getItems() {
        loading = true;
        try {
            const response = await fetch(`http://localhost:8000/search?page=${page}&limit=17`);
            const data = await response.json();
            items = data.Items || [];
            filteredItems = items;
            maxPage = data.TotalPages || 1;
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    async function getSearch(){
        loading = true;
        try {
            const response = await fetch(`http://localhost:8000/search?name=${searchQuery}&page=${page}&limit=17`);
            const data = await response.json();
            items = data.Items || [];
            filteredItems = items;
            maxPage = data.TotalPages || 1;
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(getItems);

</script>
<h1>Daftar Produk</h1>

<input type="text" placeholder="Search..." bind:value={searchQuery}/>
<button on:click={() => {
    page = 1;
    getSearch();
    }}> Search</button>
{#if loading}
    <div class="loading-container">
        <div class="spinner"></div>
        <p>Loading products...</p>
    </div>
{:else}
<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Stock</th>
            <th>Kulon</th>
            <th>Toko</th>
            <th>Pink</th>
            <th>Wetan</th>
            <th>Kedung</th>
            <th>Price</th>
            <th>Buy Price</th>
            <th>Category</th>
        </tr>
    </thead>
    <tbody>
        {#each filteredItems as item (item.result_id)}
            <tr>
                <td>{item.result_id}</td>
                <td>{item.result_name}</td>
                <td>{item.result_stock}</td>
                <td>{item.result_kulon}</td>
                <td>{item.result_toko}</td>
                <td>{item.result_pink}</td>
                <td>{item.result_wetan}</td>
                <td>{item.result_kedungsari}</td>
                <td>{item.result_price}</td>
                <td>{item.result_buy_price}</td>
                <td>{item.result_categories}</td>
            </tr>
        {/each}
    </tbody>
</table>
{/if}
<button on:click={() => {
    page = page - 1;
    if (page===0){
        page = maxPage;
        getSearch()
    }else{
        getSearch()
    }

}}>Prev</button>
<button on:click={() => {
    page = page + 1;
    if (page>maxPage){
        page = 1;
        getSearch()
    }else{
        getSearch()
    }

}}>Next</button>
<p>Total Halaman: {maxPage}</p>
<p>Halaman Saat ini: {page}</p>

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
