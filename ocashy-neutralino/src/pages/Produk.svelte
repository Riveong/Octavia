<script lang="ts">
  import { onMount } from "svelte";
  import {
    cariBarang,
    tambahBarang,
    ubahBarang,
    hapusBarang,
    totalStok,
    GUDANG,
  } from "../lib/services/produk";
  import { toast } from "../lib/stores/toast.svelte";
  import { angka } from "../lib/utils/format";
  import type { Barang, NewBarang } from "../lib/db/schema";

  let q = $state("");
  let page = $state(1);
  let totalPages = $state(1);
  let total = $state(0);
  let items = $state<Barang[]>([]);
  let loading = $state(false);
  let searchTimer: ReturnType<typeof setTimeout> | undefined;

  async function load(p = 1) {
    loading = true;
    try {
      const res = await cariBarang(q, p, 15);
      items = res.items;
      totalPages = res.totalPages;
      total = res.total;
      page = res.page;
    } catch (e) {
      toast.error(`Gagal memuat produk: ${e}`);
    } finally {
      loading = false;
    }
  }

  function onSearchInput() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => load(1), 250);
  }

  onMount(() => {
    load(1);
  });

  // --- form tambah/edit ---
  const kosong = (): NewBarang => ({
    idBarang: "",
    nama: "",
    hargaJual: 0,
    hargaBeli: 0,
    idKategori: "",
    kulon: 0,
    toko: 0,
    pink: 0,
    wetan: 0,
    kedungsari: 0,
  });

  let form = $state<NewBarang>(kosong());
  let mode = $state<"tutup" | "tambah" | "edit">("tutup");

  function bukaTambah() {
    form = kosong();
    mode = "tambah";
  }

  function bukaEdit(b: Barang) {
    form = { ...b };
    mode = "edit";
  }

  async function simpan(e: SubmitEvent) {
    e.preventDefault();
    try {
      if (mode === "tambah") {
        if (!form.idBarang.trim()) throw new Error("ID barang wajib diisi.");
        if (!form.nama.trim()) throw new Error("Nama barang wajib diisi.");
        await tambahBarang($state.snapshot(form));
        toast.success(`Produk "${form.nama}" ditambahkan.`);
      } else {
        const { idBarang, ...rest } = $state.snapshot(form);
        await ubahBarang(idBarang, rest);
        toast.success(`Produk "${form.nama}" diperbarui.`);
      }
      mode = "tutup";
      load(page);
    } catch (err) {
      toast.error(String(err instanceof Error ? err.message : err));
    }
  }

  async function hapus(b: Barang) {
    if (!confirm(`Hapus produk "${b.nama}"?`)) return;
    try {
      await hapusBarang(b.idBarang);
      toast.success(`Produk "${b.nama}" dihapus.`);
      load(page);
    } catch (e) {
      toast.error(`Gagal menghapus: ${e}`);
    }
  }
</script>

<div class="head">
  <h2>Produk <span class="muted count">({angka(total)} item)</span></h2>
  <button class="primary" onclick={bukaTambah}>+ Tambah Produk</button>
</div>

{#if mode !== "tutup"}
  <form class="card form" onsubmit={simpan}>
    <h3>{mode === "tambah" ? "Tambah Produk" : `Edit: ${form.nama}`}</h3>
    <div class="grid">
      <div>
        <label for="f-id">ID Barang</label>
        <input id="f-id" bind:value={form.idBarang} readonly={mode === "edit"} required />
      </div>
      <div class="wide">
        <label for="f-nama">Nama</label>
        <input id="f-nama" bind:value={form.nama} required />
      </div>
      <div>
        <label for="f-kategori">Kategori</label>
        <input id="f-kategori" bind:value={form.idKategori} />
      </div>
      <div>
        <label for="f-jual">Harga Jual</label>
        <input id="f-jual" type="number" min="0" bind:value={form.hargaJual} required />
      </div>
      <div>
        <label for="f-beli">Harga Beli</label>
        <input id="f-beli" type="number" min="0" bind:value={form.hargaBeli} />
      </div>
    </div>
    <h3 class="sub">Stok per gudang</h3>
    <div class="grid">
      {#each GUDANG as g (g)}
        <div>
          <label for={"f-" + g}>{g}</label>
          <input id={"f-" + g} type="number" min="0" bind:value={form[g]} />
        </div>
      {/each}
    </div>
    <div class="actions">
      <button type="button" onclick={() => (mode = "tutup")}>Batal</button>
      <button class="primary" type="submit">Simpan</button>
    </div>
  </form>
{/if}

<div class="card">
  <input type="search" placeholder="Cari produk…" bind:value={q} oninput={onSearchInput} />

  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Nama</th>
        <th>Kategori</th>
        <th class="num">Harga Jual</th>
        {#each GUDANG as g (g)}
          <th class="num">{g}</th>
        {/each}
        <th class="num">Total Stok</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {#each items as b (b.idBarang)}
        <tr>
          <td class="muted">{b.idBarang}</td>
          <td>{b.nama}</td>
          <td>{b.idKategori}</td>
          <td class="num">{angka(b.hargaJual)}</td>
          {#each GUDANG as g (g)}
            <td class="num">{b[g]}</td>
          {/each}
          <td class="num">
            <span class="badge" class:ok={totalStok(b) > 5} class:low={totalStok(b) <= 5}>
              {totalStok(b)}
            </span>
          </td>
          <td class="row-actions">
            <button class="ghost" onclick={() => bukaEdit(b)}>Edit</button>
            <button class="danger" onclick={() => hapus(b)}>Hapus</button>
          </td>
        </tr>
      {:else}
        <tr><td colspan="12" class="empty">{loading ? "Memuat…" : "Tidak ada produk."}</td></tr>
      {/each}
    </tbody>
  </table>

  <div class="pager">
    <button disabled={page <= 1} onclick={() => load(page - 1)}>‹ Prev</button>
    <span>Hal {page} / {totalPages}</span>
    <button disabled={page >= totalPages} onclick={() => load(page + 1)}>Next ›</button>
  </div>
</div>

<style>
  .head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
  }
  .count { font-size: 14px; font-weight: 400; }

  .form { margin-bottom: 16px; }
  .grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
  }
  .wide { grid-column: span 2; }
  .sub { margin-top: 14px; }
  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 14px;
  }

  .card > input[type="search"] { margin-bottom: 10px; }
  .row-actions { white-space: nowrap; }
</style>
