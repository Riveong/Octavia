<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';

  let items = []; // Holds fetched items
  let currentPage = 1; // Pagination: current page
  const itemsPerPage = 6; // Pagination: items per page
  let search = ''; // Search query
  let discountType = 'percent';

  // Fetch items from the backend
  async function getItems() {
    const response = await fetch('http://localhost:8000/barang');
    const data = await response.json();
    items = data.Items;
  }

  // Call getItems when the component mounts
  onMount(getItems);

  // Change current page for pagination
  function changePage(page) {
    currentPage = page;
  }

  // Filtered items based on search query
  $: filteredItems = items.filter(item => 
    item.result_name.toLowerCase().includes(search.toLowerCase())
  );

  // Paginated items based on current page
  $: paginatedItems = filteredItems.slice(
    (currentPage - 1) * itemsPerPage, 
    currentPage * itemsPerPage
  );


  function transferData(id, name, price, kulon, toko, pink, wetan, kedungsari) {
  // Assuming you have the form elements selected or use bind:this in Svelte
  const idInput = document.getElementById('transferId');
  const nameInput = document.getElementById('transferName');
  const warehouseSelect = document.getElementById('warehouseSelect');

  // Set the value of the form inputs
  idInput.value = id;
  nameInput.value = name;

  // Clear existing options in the select box
  warehouseSelect.innerHTML = '';

  // Array of warehouse names
  const warehouses = ['kulon: '+kulon, 'toko: '+toko,'pink: '+ pink,'wetan: '+ wetan,'kedungsari: '+ kedungsari];

  // Populate the select box with warehouse names
  warehouses.forEach(warehouse => {
    const option = document.createElement('option');
    option.value = warehouse;
    option.textContent = warehouse;
    warehouseSelect.appendChild(option);
  });
}


</script>

<!-- Search input -->
<input type="text" bind:value={search} placeholder="Search...">

<!-- Display of items with pagination -->
<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Stock</th>
      <th>Harga Satuan</th>
      <th>Action</th>
    </tr>
  </thead>
  <tbody>
    {#each paginatedItems as item (item.result_id)}
      <tr>
        <td>{item.result_name}</td>
        <td>{item.result_stock}</td>
        <td>{item.result_price}</td>
        <!-- Placeholder for future transfer functionality -->
        <td><button on:click={() => transferData(item.result_id, item.result_name, item.result_price, item.result_kulon, item.result_toko, item.result_pink, item.result_wetan, item.result_kedungsari)}>➕</button></td>
      </tr>
    {/each}
  </tbody>
</table>

<!-- Pagination navigation -->
<nav>
  <ul>
    {#each Array(Math.ceil(filteredItems.length / itemsPerPage)) as _, i}
      <li>
        <button on:click={() => changePage(i + 1)}>{i + 1}</button>
      </li>
    {/each}
  </ul>
</nav>

<h2>Selected Item</h2>
<form id="transferForm" class="form-container">
  <div>
    <label for="transferId">Item ID:</label>
    <input id="transferId" type="text" name="itemId" readonly />
  </div>
  <div>
    <label for="transferName">Item Name:</label>
    <input id="transferName" type="text" name="itemName" readonly />
  </div>
  
  <div>
    <label for="transferQuantity">Quantity:</label>
    <input id="transferQuantity" type="number" name="quantity" min="1" />
  </div>
  <div>
    <label>
      <input type="radio" name="discountType" bind:group={discountType} value="percent" />
      Discount %
    </label>
    <label>
      <input type="radio" name="discountType" bind:group={discountType} value="amount" />
      Discount #
    </label>
  </div>
  {#if discountType === 'percent'}
  <div>
    <label for="discountPercentage">Discount Percentage:</label>
    <input id="discountPercentage" type="number" name="discountPercentage" min="1" max="100" />
  </div>
{/if}

<!-- Discount Amount Input -->
{#if discountType === 'amount'}
  <div>
    <label for="discountAmount">Discount Amount:</label>
    <input id="discountAmount" type="number" name="discountAmount" min="1" />
  </div>
{/if}
  
<div>
  <label for="warehouseSelect">Warehouse:</label>
  <select id="warehouseSelect"></select>
</div>
  
  <button type="submit">Transfer</button>
</form>



<style>
  ul {
    list-style-type: none;
    margin: 0;
    padding: 0;
    overflow: hidden;
  }
  li {
    float: left;
  }
  li a {
    display: block;
    color: black;
    text-align: center;
    padding: 14px 16px;
    text-decoration: none;
  }

  .form-row {
    display: flex;
    align-items: center; /* Align items vertically in the center */
    justify-content: space-between; /* Distribute space between items */
    margin-bottom: 10px; /* Add some space between rows */
  }

  .form-row label {
    margin-right: 10px; /* Add some space between label and input */
  }

  .form-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px; /* Add gap between form groups */
  }
</style>
