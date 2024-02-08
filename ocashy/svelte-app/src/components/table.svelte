<script>
    let items = [];
    let filteredItems = [];
    let searchTerm = '';

    async function getItems() {
        const response = await fetch('http://localhost:8000/barang');
        const data = await response.json();
        items = data.Items;
        filteredItems = items;
    }

    function filterItems() {
        filteredItems = items.filter((item) => {
            // Assuming `item` has properties you are searching in.
            // Adjust the properties you want to search by.
            return item.result_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                   item.result_id.toString().includes(searchTerm) ||
                   item.result_categories.toLowerCase().includes(searchTerm.toLowerCase());
        });
    }

    $: searchTerm, filterItems(); // Reactive statement to filter items when searchTerm changes

    getItems();
</script>
<h1>Daftar Produk</h1>

<input type="text" placeholder="Search..." bind:value={searchTerm} />

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

<style>
    input[type="text"] {
        width: 100%;
        padding: 10px;
        margin-bottom: 20px;
        box-sizing: border-box;
    }
</style>
