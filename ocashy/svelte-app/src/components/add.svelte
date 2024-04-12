<script>
    import { onMount } from 'svelte';
    let item = {
      id_barang: '',
      nama: '',
      hargaJual: 0,
      hargaBeli: 0,
      id_kategori: '',
      kulon: 0,
      toko: 0,
      pink: 0,
      wetan: 0,
      kedungsari: 0
    };


  
    const handleSubmit = async () => {
      const response = await fetch('http://localhost:8000/items/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(item)  // Send item as the request body
      });
  
      if (!response.ok) {
        console.error('Failed to send data:', response.statusText);
        window.alert('ERROR! terdapat duplikasi pada id data!');
        return;
      }
  
      const result = await response.json();
      console.log('Response from server:', result);
      window.alert('data berhasil dimasukan!');
    };
    
  </script>

    <h1>Buat Produk Baru</h1>
  <form on:submit|preventDefault={handleSubmit}>
    <label>
      id_barang:
      <input type="text" bind:value={item.id_barang} />
    </label>
    <label>
      nama:
      <input type="text" bind:value={item.nama} />
    </label>
    <label>
      hargaJual:
      <input type="number" min="0" bind:value={item.hargaJual} />
    </label>
    <label>
      hargaBeli:
      <input type="number" min="0" bind:value={item.hargaBeli} />
    </label>
    <label>
      id_kategori:
      <input type="text" bind:value={item.id_kategori} />
    </label>
    <label>
      kulon:
      <input type="number" min="0" bind:value={item.kulon} />
    </label>
    <label>
      toko:
      <input type="number" min="0" bind:value={item.toko} />
    </label>
    <label>
      pink:
      <input type="number" min="0" bind:value={item.pink} />
    </label>
    <label>
      wetan:
      <input type="number" min="0" bind:value={item.wetan} />
    </label>
    <label>
      kedungsari:
      <input type="number" min="0" bind:value={item.kedungsari} />
    </label>
    <button type="submit">Submit</button>
  </form>
