<script>
    import { onMount } from 'svelte';
  
    let products = [];
    let selectedProduct = '';
    let quantity = 0;
    let discount = 0;
    let discountedAmount = 0;
    let orders = [];
    let editingIndex = -1;
    let warehouses = []; // New variable for warehouses
    let selectedWarehouse = ''; // New variable for selected warehouse
  
    const getItems = async () => {
      const response = await fetch('http://localhost:8000/barang');
      const data = await response.json();
      products = data.Items;
    };
  
    onMount(getItems);
  
    // Reactive statement to update warehouse values when selectedProduct changes
    $: if (selectedProduct) {
      const product = products.find(p => p.result_name === selectedProduct);
      warehouses = [
        {name: 'Kulon', stock: product.result_kulon},
        {name: 'Toko', stock: product.result_toko},
        {name: 'Pink', stock: product.result_pink},
        {name: 'Wetan', stock: product.result_wetan},
        {name: 'Kedungsari', stock: product.result_kedungsari}
      ];
    }
  
    const handleSubmit = () => {
      const product = products.find(p => p.result_name === selectedProduct);
      const price = product ? product.result_price * quantity : 0; // Multiply price by quantity
      const discountedPrice = price - discountedAmount;
      if (editingIndex === -1) {
        orders = [...orders, {product: selectedProduct, quantity, discount, price: discountedPrice, discountedAmount, warehouse: selectedWarehouse}];
      } else {
        orders[editingIndex] = {product: selectedProduct, quantity, discount, price: discountedPrice, discountedAmount, warehouse: selectedWarehouse};
        editingIndex = -1;
      }
      selectedProduct = '';
      quantity = 0;
      discount = 0;
      discountedAmount = 0;
      selectedWarehouse = ''; // Reset selected warehouse
    };
  
    const handleEdit = (index) => {
      selectedProduct = orders[index].product;
      quantity = orders[index].quantity;
      discount = orders[index].discount;
      discountedAmount = orders[index].discountedAmount;
      selectedWarehouse = orders[index].warehouse; // Set selected warehouse
      editingIndex = index;
    };
  
    const handleDelete = (index) => {
      orders = orders.filter((_, i) => i !== index);
    };
</script>

<h1>Buat Nota</h1>
<form on:submit|preventDefault={handleSubmit}>
  <label>
    Product:
    <select bind:value={selectedProduct}>
      <option disabled selected value=""> -- select an option -- </option>
      {#each products as product (product)}
        <option>{product.result_name}</option>
      {/each}
    </select>
  </label>
  <label>
    Quantity:
    <input type="number" min="0" bind:value={quantity} />
  </label>
  <label>
    Discount:
    <input type="number" min="0" max="100" step="0.01" bind:value={discount} on:input={() => discountedAmount = (products.find(p => p.result_name === selectedProduct)?.result_price * quantity || 1) * discount / 100} />%
  </label>
  <label>
    Discounted Amount:
    <input type="number" min="0" bind:value={discountedAmount} on:input={() => discount = ((discountedAmount / (products.find(p => p.result_name === selectedProduct)?.result_price * quantity || 1)) * 100).toFixed(2)} />
  </label>
  <label> <!-- New label for warehouse dropdown -->
    Warehouse:
    <select bind:value={selectedWarehouse}>
      <option disabled selected value=""> -- select an option -- </option>
      {#each warehouses as warehouse (warehouse)}
        <option>{warehouse.name} ({warehouse.stock})</option>
      {/each}
    </select>
  </label>
  <button type="submit">{editingIndex === -1 ? 'Submit' : 'Update'}</button>
</form>
  <br>
{#if orders.length > 0}
  <table>
    <thead>
      <tr>
        <th>Product</th>
        <th>Quantity</th>
        <th>Discount</th>
        <th>Discounted Amount</th>
        <th>Price</th>
        <th>Warehouse</th> <!-- New column for warehouse -->
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {#each orders as order, index (index)}
        <tr>
          <td>{order.product}</td>
          <td>{order.quantity}</td>
          <td>{order.discount}%</td>
          <td>{order.discountedAmount}</td>
          <td>{order.price}</td>
          <td>{order.warehouse}</td> <!-- New cell for warehouse -->
          <td>
            <button on:click={() => handleEdit(index)}>✏️</button>
            <button on:click={() => handleDelete(index)}>🗑️</button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
  <br>
  <button>Cetak</button>
{/if}
