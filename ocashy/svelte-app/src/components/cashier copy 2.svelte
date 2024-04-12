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
  const hargaSatu = document.getElementById('hargaSatuan');

  // Set the value of the form inputs
  idInput.value = id;
  nameInput.value = name;
  hargaSatu.value = price;

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


function handleTransfer(event) {
    event.preventDefault(); // Prevent the form from submitting traditionally
    
    // Assuming you have the form elements accessible, you might need to adjust selectors based on actual IDs or use Svelte bindings
    const itemName = document.getElementById('transferName').value;
    const quantity = document.getElementById('transferQuantity').value; // Ensure this ID is unique and corrected in your form
    const warehouse = document.getElementById('warehouseSelect').value;
    if (discountType==='percentage'){
      const discountPercentage = document.getElementById('discountPercentage').value;
      addRowToTable(itemName, quantity, warehouse,0,discountPercentage);
    }else{
      const discountAmount = document.getElementById('dicountAmount').value;
      addRowToTable(itemName, quantity, warehouse,discountAmount,0);
    }
    
    
  
    // Function to add the row to the table

  }

// Function to add a row to the "Transferred Items" table
function addRowToTable(itemName, quantity = 1, warehouse, discountAmount = 0, discountPercentage=0) {
  const table = document.getElementById('transferredItemsTable').getElementsByTagName('tbody')[0];
  const newRow = table.insertRow();

  // Cells for item information
  const cell1 = newRow.insertCell(0);
  const cell2 = newRow.insertCell(1);
  const cell3 = newRow.insertCell(2);
  const cell4 = newRow.insertCell(3);
  const cell5 = newRow.insertCell(4);
  const cell6 = newRow.insertCell(5);
  // Cell for delete button
  const cell7 = newRow.insertCell(6);

  cell1.textContent = itemName;
  cell2.textContent = quantity;
  cell3.textContent = discountAmount;
  cell4.textContent = discountPercentage;
  cell6.textContent = warehouse;
  

  // Create a delete button
  const deleteBtn = document.createElement('button');
  deleteBtn.textContent = '❌';
  deleteBtn.onclick = function() {
    // Call the deleteRow function and pass the current row to be deleted
    deleteRow(newRow);
  };
  cell7.appendChild(deleteBtn);
}


// Function to delete a row from the table
function deleteRow(row) {
  row.parentNode.removeChild(row);
}

</script>
<h3>Daftar Barang</h3>
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

<h3>Selected Item</h3>
<form id="transferForm" class="form-container" on:submit|preventDefault={handleTransfer}>
  <div>
    <label for="transferId">Item ID:</label>
    <input id="transferId" type="text" name="itemId" readonly />
  </div>
  <div>
    <label for="transferName">Item Name:</label>
    <input id="transferName" type="text" name="itemName" readonly />
  </div>
  <div>
    <label for="hargaSatuan">Harga Satuan:</label>
    <input id="hargaSatuan" type="text" name="itemId" readonly />
  </div>
  
  <div>
    <label for="transferQuantity">Quantity:</label>
    <input id="transferQuantity" type="number" name="quantity" min="1" required/>
  </div>
  <div>
    <label>
      <input id="disper" type="radio" name="discountType" bind:group={discountType} value="percent" />
      Discount %
    </label>
    <label>
      <input id="dismon" type="radio" name="discountType" bind:group={discountType} value="amount" />
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
  
  <button type="submit">Enter</button>
</form>

<h3>Order cart</h3>
<table id="transferredItemsTable">
  <thead>
    <tr>
      <th>Item Name</th>
      <th>Quantity</th>
      <th>Diskon (%)</th>
      <th>Diskon (#)</th>
      <th>Harga total</th>
      <th>Warehouse</th>
      <th>Action</th>
    </tr>
  </thead>
  <tbody>
    <!-- Transferred items will be added here -->
  </tbody>
</table>


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
