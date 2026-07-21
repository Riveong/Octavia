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

    let submitting = false;

    function resetForm() {
      item = {
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
    }
  
    const handleSubmit = async () => {
      if (!item.id_barang.trim() || !item.nama.trim()) {
        window.alert('Mohon isi ID Barang dan Nama Produk!');
        return;
      }

      submitting = true;
      try {
        const response = await fetch('http://localhost:8000/items/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(item)
        });
    
        if (!response.ok) {
          console.error('Failed to send data:', response.statusText);
          window.alert('ERROR! Terdapat duplikasi pada ID data atau input tidak valid!');
          return;
        }
    
        const result = await response.json();
        console.log('Response from server:', result);
        window.alert('Data produk berhasil dimasukkan!');
        resetForm();
      } catch (err) {
        console.error('Submit error:', err);
        window.alert('Terjadi kesalahan koneksi ke server!');
      } finally {
        submitting = false;
      }
    };
</script>

<div class="add-container">
    <h1>Buat Produk Baru</h1>
    
    <form on:submit|preventDefault={handleSubmit} class="product-form">
        <!-- Section 1: Informasi Produk -->
        <div class="form-section">
            <h3 class="section-title">Informasi Produk</h3>
            <div class="form-grid-three">
                <div class="form-group">
                    <label for="id_barang">ID Barang</label>
                    <input id="id_barang" type="text" placeholder="Contoh: B004" bind:value={item.id_barang} required />
                </div>
                <div class="form-group span-two">
                    <label for="nama">Nama Produk</label>
                    <input id="nama" type="text" placeholder="Masukkan nama produk..." bind:value={item.nama} required />
                </div>
            </div>
            
            <div class="form-grid-two" style="margin-top: 15px;">
                <div class="form-group">
                    <label for="id_kategori">ID Kategori</label>
                    <input id="id_kategori" type="text" placeholder="Contoh: K01" bind:value={item.id_kategori} />
                </div>
            </div>
        </div>

        <!-- Section 2: Informasi Harga -->
        <div class="form-section">
            <h3 class="section-title">Informasi Harga (Rupiah)</h3>
            <div class="form-grid-two">
                <div class="form-group">
                    <label for="hargaBeli">Harga Beli</label>
                    <div class="input-prefix-wrapper">
                        <span class="input-prefix">Rp</span>
                        <input id="hargaBeli" type="number" min="0" bind:value={item.hargaBeli} />
                    </div>
                </div>
                <div class="form-group">
                    <label for="hargaJual">Harga Jual</label>
                    <div class="input-prefix-wrapper">
                        <span class="input-prefix">Rp</span>
                        <input id="hargaJual" type="number" min="0" bind:value={item.hargaJual} />
                    </div>
                </div>
            </div>
        </div>

        <!-- Section 3: Stok Gudang/Toko -->
        <div class="form-section">
            <h3 class="section-title">Stok Lokasi</h3>
            <div class="form-grid-five">
                <div class="form-group">
                    <label for="kulon">Gudang Kulon</label>
                    <input id="kulon" type="number" min="0" bind:value={item.kulon} />
                </div>
                <div class="form-group">
                    <label for="toko">Toko</label>
                    <input id="toko" type="number" min="0" bind:value={item.toko} />
                </div>
                <div class="form-group">
                    <label for="pink">Pink</label>
                    <input id="pink" type="number" min="0" bind:value={item.pink} />
                </div>
                <div class="form-group">
                    <label for="wetan">Gudang Wetan</label>
                    <input id="wetan" type="number" min="0" bind:value={item.wetan} />
                </div>
                <div class="form-group">
                    <label for="kedungsari">Kedungsari</label>
                    <input id="kedungsari" type="number" min="0" bind:value={item.kedungsari} />
                </div>
            </div>
        </div>

        <div class="form-actions">
            <button type="button" class="btn-secondary" on:click={resetForm} disabled={submitting}>Reset Form</button>
            <button type="submit" class="btn-primary" disabled={submitting}>
                {#if submitting}
                    Sedang Menyimpan...
                {:else}
                    Simpan Produk
                {/if}
            </button>
        </div>
    </form>
</div>

<style>
    .add-container {
        width: 100%;
        box-sizing: border-box;
    }
    
    h1 {
        margin-bottom: 25px;
        color: #212529;
        font-size: 24px;
        font-weight: 700;
    }

    .product-form {
        background: transparent;
        padding: 0;
        border: none;
        box-shadow: none;
    }

    .form-section {
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 1px solid #f1f3f5;
    }

    .form-section:last-of-type {
        border-bottom: none;
        margin-bottom: 15px;
    }

    .section-title {
        font-size: 15px;
        color: #036ac4;
        font-weight: 600;
        margin-bottom: 15px;
        margin-top: 0;
        border-left: 3px solid #036ac4;
        padding-left: 10px;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    label {
        font-size: 13px;
        font-weight: 600;
        color: #495057;
    }

    input {
        padding: 10px 14px;
        border: 1px solid #ced4da;
        border-radius: 6px;
        font-size: 14px;
        color: #212529;
        transition: all 0.15s ease-in-out;
        outline: none;
    }

    input:focus {
        border-color: #036ac4;
        box-shadow: 0 0 0 3px rgba(3, 106, 196, 0.12);
    }

    /* Grids */
    .form-grid-two {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }

    .form-grid-three {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 16px;
    }

    .span-two {
        grid-column: span 2;
    }

    .form-grid-five {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 12px;
    }

    @media (max-width: 850px) {
        .form-grid-five {
            grid-template-columns: repeat(3, 1fr);
        }
    }

    @media (max-width: 650px) {
        .form-grid-three {
            grid-template-columns: 1fr;
        }
        .span-two {
            grid-column: span 1;
        }
        .form-grid-two {
            grid-template-columns: 1fr;
        }
        .form-grid-five {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    /* Input with Rp prefix */
    .input-prefix-wrapper {
        display: flex;
        align-items: stretch;
        border: 1px solid #ced4da;
        border-radius: 6px;
        overflow: hidden;
        transition: all 0.15s ease-in-out;
    }

    .input-prefix-wrapper:focus-within {
        border-color: #036ac4;
        box-shadow: 0 0 0 3px rgba(3, 106, 196, 0.12);
    }

    .input-prefix {
        background: #f1f3f5;
        color: #495057;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        padding: 0 12px;
        border-right: 1px solid #ced4da;
    }

    .input-prefix-wrapper input {
        border: none;
        flex-grow: 1;
        padding-left: 10px;
        border-radius: 0;
    }

    .input-prefix-wrapper input:focus {
        box-shadow: none;
    }

    /* Form Actions */
    .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-top: 10px;
    }

    button {
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 600;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.15s ease-in-out;
        border: 1px solid transparent;
    }

    .btn-primary {
        background-color: #036ac4;
        color: #ffffff;
    }

    .btn-primary:hover:not(:disabled) {
        background-color: #025299;
    }

    .btn-secondary {
        background-color: #ffffff;
        border-color: #ced4da;
        color: #495057;
    }

    .btn-secondary:hover:not(:disabled) {
        background-color: #f8f9fa;
        border-color: #adb5bd;
    }

    button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
</style>
