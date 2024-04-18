<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';

  let items = []; // Holds fetched items
  let currentPage = 1; // Pagination: current page
  const itemsPerPage = 99; // Pagination: items per page
  let search = ''; // Search query
  let page = 1;
  let maxPage;
  let discountType = 'percent';
  let show = false;
  let notShow = true;


  function hide() {
	show = !show;
  notShow = !notShow;
  }
  

  // Fetch items from the backend
  async function getItems() {
    const response = await fetch(`http://localhost:8000/search?page=${page}&limit=8`);
    const data = await response.json();
    items = data.Items;
    maxPage = data.TotalPages;
  }
  
  async function getSearch(){
        const search = document.getElementById('search').value;
        const response = await fetch(`http://localhost:8000/search?name=${search}&page=${page}&limit=8`);
        const data = await response.json();
        items = data.Items;
        filteredItems = items;
        maxPage = data.TotalPages;
    }
  // Call getItems when the component mounts
  onMount(getItems);


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
    const quantity = document.getElementById('transferQuantity').value;
    const hargaSatuan = document.getElementById('hargaSatuan').value; // Ensure this ID is unique and corrected in your form
    const warehouse1 = document.getElementById('warehouseSelect').value;
    const warehouse = warehouse1.replace(/:\s*\d+$/, '');
    if (discountType==='percent'){
      const discountPercentage = document.getElementById('discountPercentage').value;
      addRowToTable(itemName, hargaSatuan, quantity, warehouse,null,discountPercentage);
    }else{
      const discountAmount = document.getElementById('discountAmount').value;
      addRowToTable(itemName, hargaSatuan, quantity, warehouse,discountAmount,null);
    }
    
    
  
    // Function to add the row to the table

  }

// Function to add a row to the "Transferred Items" table
function addRowToTable(itemName, hargaSatuan, quantity = 1, warehouse, discountAmount = null, discountPercentage=null) {
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



  //hitung diskon + total harga  
  const totalHarga = quantity * hargaSatuan
  let persen = discountPercentage
  let amount = discountAmount

  if (persen === null){
    persen = (discountAmount / totalHarga) * 100;
  }
  if (amount === null){
    amount = (totalHarga * discountPercentage) / 100;
  }
  const finalHarga = totalHarga - amount;



  cell1.textContent = itemName;
  cell2.textContent = quantity;
  cell3.textContent = persen+'%';
  cell4.textContent = amount;
  cell5.textContent = finalHarga;
  cell6.textContent = warehouse;
  

  // Create a delete button
  const deleteBtn = document.createElement('button');
  deleteBtn.textContent = '❌';
  deleteBtn.onclick = function() {
    // Call the deleteRow function and pass the current row to be deleted
    deleteRow(newRow);
  };
  cell7.appendChild(deleteBtn);

  updateTotalSum()
}


// Function to delete a row from the table
function deleteRow(row) {
  row.parentNode.removeChild(row);
  updateTotalSum()
}



function submitNota() {
  // Get the table's tbody element
  const nominal = document.getElementById('nomu').value;
  const tipe = document.getElementById('tipe').value;
  const tableBody = document.getElementById('transferredItemsTable').getElementsByTagName('tbody')[0];
  
  // Check if the table has no rows
  if (tableBody.rows.length === 0) {
    alert("tabel tidak memiliki data!");
    return; // Stop the function execution
  }

  const notaData = []; // Array to hold the data from each row
  
  for (let row of tableBody.rows) {
    // Check for empty strings or null values in cells
    for (let cell of row.cells) {
      if (cell.textContent.trim() === "" || cell.textContent === null) {
        alert("satu atau lebih baris terdapat data yang kosong!");
        return; // Stop the function execution
      }
    }

    // Assuming the order of cells is: Item Name, Quantity, Diskon (%), Diskon (#), Harga total, Warehouse
    const rowData = {
      itemName: row.cells[0].textContent,
      quantity: parseInt(row.cells[1].textContent),
      discountPercentage: parseInt(row.cells[2].textContent.slice(0, -1)),
      discountAmount: parseInt(row.cells[3].textContent),
      totalPrice: row.cells[4].textContent,
      warehouse: row.cells[5].textContent
    };

    notaData.push(rowData);

    
  }

  // Proceed if there are no issues
  console.log(nominal);
  console.log(notaData);
  pushApi(nominal, notaData, tipe)
}

async function pushApi(nominal, notaData, tipe) {
  try {
    const response = await fetch(`http://localhost:8000/items/${nominal}/${tipe}`, {
      method: 'POST', // Specify the request method
      headers: {
        'Content-Type': 'application/json', // Specify the content type as JSON
      },
      body: JSON.stringify(notaData), // Convert the notaData object to a JSON string
    });

    if (!response.ok) {
      // If the response is not OK, throw an error
      throw new Error(`Error: ${response.statusText}`);
    }

    const responseData = await response.json(); // Assuming the server responds with JSON
    console.log('Success:', responseData); // Log the success and response data
    alert('Data successfully submitted!'); // Notify the user of success
    window.open(responseData.response);
  } catch (error) {
    console.error('Error:', error); // Log any errors to the console
    alert(`Failed to submit data: ${error.message}`); // Notify the user of the error
  }
}

function updateTotalSum() {
  const tableBody = document.getElementById('transferredItemsTable').getElementsByTagName('tbody')[0];
  let totalSum = 0;

  for (let row of tableBody.rows) {
    const hargaTotalCellText = row.cells[4].textContent; // Assuming the 'Harga total' is in the fifth column
    const hargaTotal = parseFloat(hargaTotalCellText.replace(/[^0-9.-]+/g, "")); // Remove any non-numeric characters, if any

    if (!isNaN(hargaTotal)) {
      totalSum += hargaTotal;
    }
  }

  // Update the display
  const totalSumDisplay = document.getElementById('totalSumDisplay');
  totalSumDisplay.textContent = `Total Nominal: ${totalSum.toLocaleString()}`; // Format to local currency, if desired
}



</script>
<h3>Daftar Barang</h3>
<!-- Search input -->
<input type="text" id = "search" placeholder="Search...">
<button on:click={() => {
  page = 1;
  getSearch();
  }}> Search</button>

  <button class:show on:click={() => {hide()}}> ➖ Tutup Table</button>
  <button class:notShow on:click={() => {hide()}}>➕ Buka Table</button>


<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Stock</th>
      <th>Harga Satuan</th>
      <th>Action</th>
    </tr>
  </thead>
  <tbody class:show>
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
<p>Halaman Saat ini: {page}</p>
<p>Total Halaman: {maxPage}</p>
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
    <input id="hargaSatuan" type="text" name="itemSatuan" readonly />
  </div>
  
  <div>
    <label for="transferQuantity">Jumlah:</label>
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
    <input id="discountPercentage" type="number" name="discountPercentage" min="0" max="100" value="0" />
  </div>
{/if}

<!-- Discount Amount Input -->
{#if discountType === 'amount'}
  <div>
    <label for="discountAmount">Discount Amount:</label>
    <input id="discountAmount" type="number" name="discountAmount" min="0" value="0"/>
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
<p id="totalSumDisplay">Total Nominal: 0</p>
<label>
  Tipe pembeli
  <input id="tipe" name="tipe"  value="Umum" />
  
</label>
<label>
  Nominal Uang
  <input id="nomu" type="number" name="nomu"  value="0" />
  
</label>
<button  on:click={() => submitNota()}>Cetak Nota</button>



<style>
  .show{
        display: none;
    }
    .notShow{
        display: none;
    }
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
