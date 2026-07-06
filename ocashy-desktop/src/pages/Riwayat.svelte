<script lang="ts">
  import { onMount } from "svelte";
  import { daftarNota, ambilNota, hapusNota } from "../lib/services/nota";
  import { getPrintSettings } from "../lib/services/settings";
  import { cetakNota } from "../lib/pdf/receipt";
  import { toast } from "../lib/stores/toast.svelte";
  import { rupiah, tanggal, angka } from "../lib/utils/format";
  import type { Nota } from "../lib/db/schema";
  import type { NotaLengkap } from "../lib/services/nota";

  let q = $state("");
  let page = $state(1);
  let totalPages = $state(1);
  let items = $state<Nota[]>([]);
  let loading = $state(false);
  let detail = $state<NotaLengkap | null>(null);
  let searchTimer: ReturnType<typeof setTimeout> | undefined;

  async function load(p = 1) {
    loading = true;
    try {
      const res = await daftarNota(q, p, 15);
      items = res.items;
      totalPages = res.totalPages;
      page = res.page;
    } catch (e) {
      toast.error(`Gagal memuat riwayat: ${e}`);
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

  async function lihat(n: Nota) {
    const d = await ambilNota(n.id);
    if (d) detail = d;
  }

  async function cetakUlang(n: Nota) {
    try {
      const d = await ambilNota(n.id);
      if (!d) throw new Error("Nota tidak ditemukan.");
      const s = await getPrintSettings();
      await cetakNota(d, s);
      toast.success(`Nota ${n.nomorFaktur} dicetak ulang.`);
    } catch (e) {
      toast.error(`Gagal cetak ulang: ${e}`);
    }
  }

  async function hapus(n: Nota) {
    if (!confirm(`Hapus nota ${n.nomorFaktur}? Stok TIDAK dikembalikan otomatis.`)) return;
    try {
      await hapusNota(n.id);
      if (detail?.nota.id === n.id) detail = null;
      toast.success("Nota dihapus.");
      load(page);
    } catch (e) {
      toast.error(`Gagal menghapus: ${e}`);
    }
  }
</script>

<h2>Riwayat Nota</h2>

<div class="layout">
  <div class="card">
    <input type="search" placeholder="Cari nomor faktur…" bind:value={q} oninput={onSearchInput} />

    <table>
      <thead>
        <tr>
          <th>No. Faktur</th>
          <th>Waktu</th>
          <th>Tipe</th>
          <th class="num">Total</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each items as n (n.id)}
          <tr class:selected={detail?.nota.id === n.id}>
            <td><button class="ghost link" onclick={() => lihat(n)}>{n.nomorFaktur}</button></td>
            <td>{tanggal(n.waktu)}</td>
            <td>{n.tipePembeli}</td>
            <td class="num"><b>{angka(n.total)}</b></td>
            <td class="row-actions">
              <button class="ghost" onclick={() => cetakUlang(n)}>🖨️ Cetak</button>
              <button class="danger" onclick={() => hapus(n)}>✕</button>
            </td>
          </tr>
        {:else}
          <tr><td colspan="5" class="empty">{loading ? "Memuat…" : "Belum ada nota tersimpan."}</td></tr>
        {/each}
      </tbody>
    </table>

    <div class="pager">
      <button disabled={page <= 1} onclick={() => load(page - 1)}>‹ Prev</button>
      <span>Hal {page} / {totalPages}</span>
      <button disabled={page >= totalPages} onclick={() => load(page + 1)}>Next ›</button>
    </div>
  </div>

  {#if detail}
    <div class="card detail">
      <div class="detail-head">
        <h3>{detail.nota.nomorFaktur}</h3>
        <button class="ghost" onclick={() => (detail = null)}>✕ Tutup</button>
      </div>
      <p class="muted">{tanggal(detail.nota.waktu)} · {detail.nota.tipePembeli}</p>
      <table>
        <thead>
          <tr>
            <th>Produk</th>
            <th class="num">Qty</th>
            <th class="num">Diskon</th>
            <th class="num">Jumlah</th>
          </tr>
        </thead>
        <tbody>
          {#each detail.items as it (it.id)}
            <tr>
              <td>{it.nama}<div class="muted small">{angka(it.hargaSatuan)} · {it.gudang}</div></td>
              <td class="num">{angka(it.qty)}</td>
              <td class="num">{angka(it.diskonTotal)}</td>
              <td class="num">{angka(it.total)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
      <div class="sums">
        <div><span>Total</span><b>{rupiah(detail.nota.total)}</b></div>
        <div><span>Bayar</span><b>{rupiah(detail.nota.bayar)}</b></div>
        <div>
          <span>{detail.nota.kembalian >= 0 ? "Kembalian" : "Kurang"}</span>
          <b>{rupiah(Math.abs(detail.nota.kembalian))}</b>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .layout {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
  }
  .layout:has(.detail) {
    grid-template-columns: 1fr minmax(340px, 420px);
    align-items: start;
  }

  .card > input[type="search"] { margin-bottom: 10px; }
  tr.selected { background: var(--primary-soft); }
  .link { padding: 0; font-weight: 600; color: var(--primary); }
  .row-actions { white-space: nowrap; }
  .small { font-size: 12px; }

  .detail-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .sums {
    border-top: 2px solid var(--border);
    margin-top: 10px;
    padding-top: 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .sums div { display: flex; justify-content: space-between; }
</style>
