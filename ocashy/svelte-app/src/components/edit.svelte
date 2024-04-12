<script>
    import { onMount } from 'svelte';
    let items = [];
    let filteredItems = [];
    let searchTerm = '';
    let editingItemId = null; // ID of the item currently being edited
    let editingItem = {}; // Object to hold the editing item's data for binding to form inputs

    async function getItems() {
        const response = await fetch('http://localhost:8000/barang');
        const data = await response.json();
        items = data.Items;
        filteredItems = items;
    }

    function filterItems() {
        filteredItems = items.filter((item) => {
            return item.result_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                   item.result_id.toString().includes(searchTerm) ||
                   item.result_categories.toLowerCase().includes(searchTerm.toLowerCase());
        });
    }

    function startEditing(item) {
        editingItemId = item.result_id;
        editingItem = { ...item }; // Clone the item for editing
    }

    async function deleteItem(item) {
    // Display a confirmation dialog
    let confirmation = window.confirm('Are you sure you want to delete this item?');

    if (confirmation) {
        console.log('Yes');
        const response = await fetch(`http://localhost:8000/items/${item.result_id}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            console.error('Failed to delete item:', response.statusText);
            return;
        }

        console.log('Item was successfully deleted.');
        getItems(); // Refresh the list

    } else {
        console.log('No');
    }
    }

    async function submitEdit() {
        // Prepare your edit submission here, converting item fields to your API's expected format
        const payload = {
            id_barang: editingItemId,
            nama: editingItem.result_name,
            hargaJual: editingItem.result_price,
            hargaBeli: editingItem.result_buy_price,
            id_kategori: editingItem.result_categories,
            kulon: editingItem.result_kulon,
            toko: editingItem.result_toko,
            pink: editingItem.result_pink,
            wetan: editingItem.result_wetan,
            kedungsari: editingItem.result_kedungsari
        };

        const response = await fetch(`http://localhost:8000/update-item/${editingItemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (response.ok) {
            getItems(); // Refresh the list
            editingItemId = null; // Exit editing mode
        }
    }

    $: searchTerm, filterItems(); // Reactively filter items on searchTerm change
    onMount(() => {
        getItems();
    });
</script>

<h1>Edit Data</h1>
<input type="text" placeholder="Search..." bind:value={searchTerm} class="search-bar" />


<div class = "scrollable-body">
<table class = "edit">
    <thead class="sticky-header">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Price</th>
            <th>Buy Price</th>
            <th>Category</th>
            <th>Kulon</th>
            <th>Toko</th>
            <th>Pink</th>
            <th>Wetan</th>
            <th>Kedung</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {#each filteredItems as item (item.result_id)}
            <tr>
                <td>{item.result_id}</td>
                {#if editingItemId === item.result_id}
                    <td><input type="text" bind:value={editingItem.result_name} /></td>
                    <td><input type="number" bind:value={editingItem.result_price} /></td>
                    <td><input type="number" bind:value={editingItem.result_buy_price} /></td>
                    <td><input type="text" bind:value={editingItem.result_categories} /></td>
                    <td><input class="int-field" type="number" bind:value={editingItem.result_kulon} /></td>
                    <td><input class="int-field" type="number" bind:value={editingItem.result_toko} /></td>
                    <td><input class="int-field" type="number" bind:value={editingItem.result_pink} /></td>
                    <td><input class="int-field" type="number" bind:value={editingItem.result_wetan} /></td>
                    <td><input class="int-field" type="number" bind:value={editingItem.result_kedungsari} /></td>
                    <td>
                        <button on:click={submitEdit}>Save</button>
                        <button on:click={() => editingItemId = null}>Cancel</button>
                    </td>
                {:else}
                    <td>{item.result_name}</td>
                    <td>{item.result_price}</td>
                    <td>{item.result_buy_price}</td>
                    <td>{item.result_categories}</td>
                    <td>{item.result_kulon}</td>
                    <td>{item.result_toko}</td>
                    <td>{item.result_pink}</td>
                    <td>{item.result_wetan}</td>
                    <td>{item.result_kedungsari}</td>
                    <td>
                        <button on:click={() => startEditing(item)}>✏️</button>
                        <button on:click={() => deleteItem(item)}>🚫</button>

                    </td>
                {/if}
            </tr>
        {/each}
    </tbody>
</table>
</div>

<style>
    .search-bar {
        width: 100%;
        padding: 10px;
        margin-bottom: 20px;
        box-sizing: border-box;
    }
    input, button {
        margin: 4px;
        padding: 8px;
    }
    button {
        cursor: pointer;
    }
    .int-field{
        max-width: 50px;
    }
    
    .scrollable-body {
        max-height: 700px; /* Adjust this value based on your needs */
        overflow-y: auto;
        display: block;
    }
    .sticky-header tr {
        position: sticky;
        top: 0;
        background: white;
        z-index: 100;
        background-color: #036ac4;
    }
    .edit {
        overflow: auto;
    }
</style>

