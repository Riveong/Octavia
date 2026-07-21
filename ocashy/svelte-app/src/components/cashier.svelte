<script>
  import { onMount } from 'svelte';

  let items = []; // Product list fetched from backend
  let page = 1;
  let maxPage = 1;
  let searchQuery = '';
  let isTableOpen = true;

  // Selected item form values
  let selectedId = '';
  let selectedName = '';
  let selectedPrice = 0;
  let quantity = 1;
  let discountType = 'percent'; // 'percent' or 'amount'
  let discountPercentage = 0;
  let discountAmount = 0;
  let availableWarehouses = []; // { name, stock }
  let selectedWarehouse = '';

  // Order cart (list of added items)
  let orderCart = [];
  let tipePembeli = 'Umum';
  let nominalUang = 0;
  let silentPrintEnabled = true;
  let loading = false;

  // Fetch initial items
  async function getItems() {
    loading = true;
    try {
      const response = await fetch(`http://localhost:8000/search?page=${page}&limit=8`);
      const data = await response.json();
      items = data.Items || [];
      maxPage = data.TotalPages || 1;
    } catch (e) {
      console.error("Failed to fetch items:", e);
    } finally {
      loading = false;
    }
  }

  // Fetch search results
  async function getSearch() {
    loading = true;
    try {
      const response = await fetch(`http://localhost:8000/search?name=${searchQuery}&page=${page}&limit=8`);
      const data = await response.json();
      items = data.Items || [];
      maxPage = data.TotalPages || 1;
    } catch (e) {
      console.error("Failed to search items:", e);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    getItems();
    const storedSilent = localStorage.getItem('silentPrintEnabled');
    if (storedSilent !== null) {
      silentPrintEnabled = storedSilent === 'true';
    }
  });

  // Pagination actions
  function prevPage() {
    page = page - 1;
    if (page < 1) {
      page = maxPage;
    }
    getSearch();
  }

  function nextPage() {
    page = page + 1;
    if (page > maxPage) {
      page = 1;
    }
    getSearch();
  }

  // Click on a product to populate the form
  function selectItem(item) {
    selectedId = item.result_id;
    selectedName = item.result_name;
    selectedPrice = item.result_price;
    quantity = 1;
    discountPercentage = 0;
    discountAmount = 0;

    // Populate warehouses
    availableWarehouses = [
      { name: 'kulon', stock: item.result_kulon },
      { name: 'toko', stock: item.result_toko },
      { name: 'pink', stock: item.result_pink },
      { name: 'wetan', stock: item.result_wetan },
      { name: 'kedungsari', stock: item.result_kedungsari }
    ];

    // Auto-select first warehouse with stock
    const firstWithStock = availableWarehouses.find(w => w.stock > 0);
    selectedWarehouse = firstWithStock ? firstWithStock.name : availableWarehouses[0].name;
  }

  // Toggle catalog table
  function toggleTable() {
    isTableOpen = !isTableOpen;
  }

  // Handle selected product form submission
  function handleTransfer() {
    if (!selectedId) {
      alert("Silakan pilih produk dari daftar barang terlebih dahulu!");
      return;
    }

    const totalHargaRaw = quantity * selectedPrice;
    let unitDiscount = 0;
    let totalDiscount = 0;
    let finalHarga = 0;

    if (discountType === 'percent') {
      unitDiscount = selectedPrice * (discountPercentage / 100);
      totalDiscount = totalHargaRaw * (discountPercentage / 100);
      finalHarga = totalHargaRaw - totalDiscount;
    } else {
      unitDiscount = discountAmount;
      totalDiscount = discountAmount * quantity;
      finalHarga = totalHargaRaw - totalDiscount;
    }

    // Add to cart
    orderCart = [...orderCart, {
      itemName: selectedName,
      satuanHarga: selectedPrice,
      quantity: quantity,
      discountPercentage: discountType === 'percent' ? discountPercentage : 0,
      discountAmount: unitDiscount, // discount per unit
      totalDiscount: totalDiscount, // total discount for row
      totalPrice: finalHarga,
      warehouse: selectedWarehouse
    }];

    // Reset selected product form
    selectedId = '';
    selectedName = '';
    selectedPrice = 0;
    quantity = 1;
    discountPercentage = 0;
    discountAmount = 0;
    availableWarehouses = [];
    selectedWarehouse = '';
  }

  // Delete item from cart
  function deleteRow(index) {
    orderCart = orderCart.filter((_, i) => i !== index);
  }

  // Reactive total sum
  $: totalSum = orderCart.reduce((sum, item) => sum + item.totalPrice, 0);

  // Submit the transaction (cetak nota)
  async function submitNota() {
    if (orderCart.length === 0) {
      alert("Tabel order cart tidak memiliki data!");
      return;
    }

    const notaData = orderCart.map(item => ({
      itemName: item.itemName,
      satuanHarga: item.satuanHarga,
      quantity: item.quantity,
      discountPercentage: item.discountPercentage,
      discountAmount: item.totalDiscount, // total discount for backend
      totalPrice: item.totalPrice,
      warehouse: item.warehouse
    }));

    try {
      const response = await fetch(`http://localhost:8000/items/${nominalUang}/${tipePembeli}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(notaData),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const responseData = await response.json();
      console.log('Success:', responseData);
      alert('Data successfully submitted!');
      window.open(responseData.response);
    } catch (error) {
      console.error('Error submitting order:', error);
      alert(`Failed to submit data: ${error.message}`);
    }
  }

  // Submit the transaction and print directly via SumatraPDF
  async function submitNotaLangsung() {
    if (orderCart.length === 0) {
      alert("Tabel order cart tidak memiliki data!");
      return;
    }

    const notaData = orderCart.map(item => ({
      itemName: item.itemName,
      satuanHarga: item.satuanHarga,
      quantity: item.quantity,
      discountPercentage: item.discountPercentage,
      discountAmount: item.totalDiscount,
      totalPrice: item.totalPrice,
      warehouse: item.warehouse
    }));

    try {
      // 1. Generate the PDF
      const response = await fetch(`http://localhost:8000/items/${nominalUang}/${tipePembeli}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(notaData),
      });

      if (!response.ok) {
        throw new Error(`Error generating PDF: ${response.statusText}`);
      }

      const responseData = await response.json();
      console.log('PDF Generated:', responseData);

      // Extract filename from response URL
      const pdfUrl = responseData.response;
      const filename = pdfUrl.substring(pdfUrl.lastIndexOf('/') + 1);

      // 2. Call the print API
      const printResponse = await fetch(`http://localhost:8000/print-pdf?filename=${encodeURIComponent(filename)}`, {
        method: 'POST',
      });

      if (!printResponse.ok) {
        const errorData = await printResponse.json();
        throw new Error(errorData.detail || `Printing error: ${printResponse.statusText}`);
      }

      alert('Nota successfully printed!');
    } catch (error) {
      console.error('Error printing order:', error);
      alert(`Failed to print: ${error.message}`);
    }
  }
</script>

<h3>Daftar Barang</h3>

<div class="search-section">
  <input type="text" placeholder="Search..." bind:value={searchQuery}>
  <button on:click={() => { page = 1; getSearch(); }}>Search</button>
  <button on:click={toggleTable}>
    {#if isTableOpen}
      ➖ Tutup Table
    {:else}
      ➕ Buka Table
    {/if}
  </button>
</div>

{#if isTableOpen}
  {#if loading}
    <div class="loading-container">
      <div class="spinner"></div>
      <p>Loading items...</p>
    </div>
  {:else}
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
        {#each items as item (item.result_id)}
          <tr>
            <td>{item.result_name}</td>
            <td>{item.result_stock}</td>
            <td>{item.result_price}</td>
            <td><button on:click={() => selectItem(item)}>➕</button></td>
          </tr>
        {/each}
      </tbody>
    </table>

    <div class="pagination">
      <button on:click={prevPage}>Prev</button>
      <span>Halaman Saat ini: {page} / {maxPage}</span>
      <button on:click={nextPage}>Next</button>
    </div>
  {/if}
{/if}

<h3>Selected Item</h3>
<form class="form-container" on:submit|preventDefault={handleTransfer}>
  <div>
    <label for="transferId">Item ID:</label>
    <input id="transferId" type="text" value={selectedId} readonly />
  </div>
  <div>
    <label for="transferName">Item Name:</label>
    <input id="transferName" type="text" value={selectedName} readonly />
  </div>
  <div>
    <label for="hargaSatuan">Harga Satuan:</label>
    <input id="hargaSatuan" type="text" value={selectedPrice} readonly />
  </div>
  
  <div>
    <label for="transferQuantity">Jumlah:</label>
    <input id="transferQuantity" type="number" bind:value={quantity} min="1" required/>
  </div>
  <div>
    <label>
      <input type="radio" bind:group={discountType} value="percent" />
      Discount %
    </label>
    <label>
      <input type="radio" bind:group={discountType} value="amount" />
      Discount #
    </label>
  </div>
  
  {#if discountType === 'percent'}
    <div>
      <label for="discountPercentage">Discount Percentage:</label>
      <input id="discountPercentage" type="number" bind:value={discountPercentage} step="any" min="0" max="100" />
    </div>
  {/if}

  {#if discountType === 'amount'}
    <div>
      <label for="discountAmount">Discount Amount:</label>
      <input id="discountAmount" type="number" bind:value={discountAmount} min="0" />
    </div>
  {/if}
  
  <div>
    <label for="warehouseSelect">Warehouse:</label>
    <select id="warehouseSelect" bind:value={selectedWarehouse}>
      {#each availableWarehouses as wh}
        <option value={wh.name}>{wh.name}: {wh.stock}</option>
      {/each}
    </select>
  </div>
  
  <button type="submit">Enter</button>
</form>

<h3>Order cart</h3>
<table id="transferredItemsTable">
  <thead>
    <tr>
      <th>Item Name</th>
      <th>Harga Satuan</th>
      <th>Quantity</th>
      <th>Diskon Satuan</th>
      <th>Total Diskon</th>
      <th>Harga total</th>
      <th>Warehouse</th>
      <th>Action</th>
    </tr>
  </thead>
  <tbody>
    {#each orderCart as item, i}
      <tr>
        <td>{item.itemName}</td>
        <td>{item.satuanHarga.toLocaleString('id-ID')}</td>
        <td>{item.quantity}</td>
        <td>{item.discountAmount.toLocaleString('id-ID')}</td>
        <td>{item.totalDiscount.toLocaleString('id-ID')}</td>
        <td>{item.totalPrice.toLocaleString('id-ID')}</td>
        <td>{item.warehouse}</td>
        <td><button type="button" on:click={() => deleteRow(i)}>❌</button></td>
      </tr>
    {/each}
  </tbody>
</table>

<p id="totalSumDisplay">Total Nominal: {totalSum.toLocaleString('id-ID')}</p>

<div class="submission-form">
  <label>
    Tipe pembeli
    <input bind:value={tipePembeli} />
  </label>
  <label>
    Nominal Uang
    <input type="number" bind:value={nominalUang} min="0" />
  </label>
  <button on:click={submitNota}>Cetak Nota</button>
  {#if silentPrintEnabled}
    <button class="btn-print-direct" on:click={submitNotaLangsung}>Cetak Nota Langsung</button>
  {/if}
</div>

<style>
  .search-section {
    margin-bottom: 15px;
    display: flex;
    gap: 10px;
    align-items: center;
  }
  .pagination {
    margin-top: 10px;
    display: flex;
    gap: 15px;
    align-items: center;
  }
  .form-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    background: #f9f9f9;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
  }
  .form-container div {
    display: flex;
    flex-direction: column;
  }
  .form-container label {
    margin-bottom: 5px;
    font-weight: bold;
  }
  .submission-form {
    margin-top: 20px;
    display: flex;
    gap: 20px;
    align-items: flex-end;
  }
  .submission-form label {
    display: flex;
    flex-direction: column;
    font-weight: bold;
  }
  input, select, button {
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  button {
    background-color: #036ac4;
    color: white;
    font-weight: bold;
    cursor: pointer;
  }
  button:hover {
    background-color: #025299;
  }
  button.btn-print-direct {
    background-color: #28a745;
  }
  button.btn-print-direct:hover {
    background-color: #218838;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
  }
  th, td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
  }
  th {
    background-color: #036ac4;
    color: white;
    font-weight: 600;
  }
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 30px;
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
