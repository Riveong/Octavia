<script>
    import { onMount } from "svelte";

    let items = [];
    let filteredItems = [];
    let page = 1;
    let maxPage;



    async function getItems() {
        const response = await fetch(`http://localhost:8000/search?page=${page}&limit=17`);
        const data = await response.json();
        items = data.Items;
        filteredItems = items;
        maxPage = data.TotalPages
    }


    async function getSearch(){
        const search = document.getElementById('search').value;
        const response = await fetch(`http://localhost:8000/search?name=${search}&page=${page}&limit=17`);
        const data = await response.json();
        items = data.Items;
        filteredItems = items;
        maxPage = data.TotalPages

    }

    onMount(getItems)

</script>
<h1>Daftar Produk</h1>

<input type="text" id = "search" placeholder="Search..."/>
<button on:click={() => {
    page = 1;
    getSearch();
    }}> Search</button>
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
</style>
