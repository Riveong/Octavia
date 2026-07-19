<script lang="ts">
  import { onMount, tick } from "svelte";
  import { cariBarang, totalStok, GUDANG, type Gudang } from "../lib/services/produk";
  import { simpanNota } from "../lib/services/nota";
  import { getPrintSettings } from "../lib/services/settings";
  import { cetakNota } from "../lib/pdf/receipt";
  import { cart, type DiskonMode } from "../lib/stores/cart.svelte";
  import { toast } from "../lib/stores/toast.svelte";
  import { rupiah, angka } from "../lib/utils/format";
  import type { Barang } from "../lib/db/schema";

  // --- pencarian produk ---
  let q = $state("");
  let page = $state(1);
  let totalPages = $state(1);
  let results = $state<Barang[]>([]);
  let loading = $state(false);
  let searchTimer: ReturnType<typeof setTimeout> | undefined;

  async function search(p = 1) {
    loading = true;
    try {
      const res = await cariBarang(q, p, 8);
      results = res.items;
      totalPages = res.totalPages;
      page = res.page;
    } catch (e) {
      toast.error(`Gagal memuat produk: ${e}`);
    } finally {
      loading = false;
    }
  }

  function onSearchInput() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => search(1), 250);
  }

  onMount(() => {
    search(1);
  });

  // --- item terpilih ---
  let selected = $state<Barang | null>(null);
  let qty = $state(1);
  let gudang = $state<Gudang>("toko");
  let diskonMode = $state<DiskonMode>("persen");
  let diskonValue = $state(0);
  let qtyInput = $state<HTMLInputElement | null>(null);

  async function pilih(b: Barang) {
    selected = b;
    qty = 1;
    diskonValue = 0;
    // gudang default: yang stoknya paling banyak
    gudang = GUDANG.reduce((best, g) => (b[g] > b[best] ? g : best), "toko" as Gudang);
    await tick(); // tunggu form item ter-render dulu
    qtyInput?.focus();
    qtyInput?.select();
  }

  function tambahKeKeranjang(e: SubmitEvent) {
    e.preventDefault();
    if (!selected) {
      toast.error("Pilih produk dulu dari daftar.");
      return;
    }
    if (qty < 1) return;
    if (diskonMode === "persen" && (diskonValue < 0 || diskonValue > 100)) {
      toast.error("Diskon persen harus 0–100.");
      return;
    }
    cart.add(selected, qty, gudang, diskonMode, diskonValue);
    selected = null;
  }

  // --- pembayaran ---
  let tipePembeli = $state("Umum");
  let bayar = $state(0);
  let saving = $state(false);

  const kembalian = $derived(bayar - cart.total);

  async function cetak() {
    if (cart.count === 0) {
      toast.error("Keranjang masih kosong.");
      return;
    }
    saving = true;
    try {
      const saved = await simpanNota({
        tipePembeli,
        bayar,
        lines: $state.snapshot(cart.lines),
      });
      const settings = await getPrintSettings();
      const path = await cetakNota(saved, settings);
      toast.success(`Nota ${saved.nota.nomorFaktur} tersimpan & dicetak ke PDF.`);
      console.info("PDF:", path);
      cart.clear();
      bayar = 0;
      tipePembeli = "Umum";
      search(page); // refresh stok di daftar
    } catch (e) {
      toast.error(`Gagal menyimpan nota: ${e}`);
    } finally {
      saving = false;
    }
  }
</script>

<h2>Kasir</h2>

<div class="layout">
  <!-- kiri: katalog + form item -->
  <section class="left">
    <div class="card">
      <div class="search-bar">
        <input
          type="search"
          placeholder="Cari produk… (ketik untuk mencari)"
          bind:value={q}
          oninput={onSearchInput}
        />
      </div>

      <table>
        <thead>
          <tr>
            <th>Produk</th>
            <th class="num">Stok</th>
            <th class="num">Harga</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each results as b (b.idBarang)}
            <tr class:selected={selected?.idBarang === b.idBarang}>
              <td>{b.nama}</td>
              <td class="num">
                <span class="badge" class:ok={totalStok(b) > 5} class:low={totalStok(b) <= 5}>
                  {totalStok(b)}
                </span>
              </td>
              <td class="num">{angka(b.hargaJual)}</td>
              <td><button class="ghost" onclick={() => pilih(b)}>+ Pilih</button></td>
            </tr>
          {:else}
            <tr><td colspan="4" class="empty">{loading ? "Memuat…" : "Tidak ada produk."}</td></tr>
          {/each}
        </tbody>
      </table>

      <div class="pager">
        <button disabled={page <= 1} onclick={() => search(page - 1)}>‹ Prev</button>
        <span>Hal {page} / {totalPages}</span>
        <button disabled={page >= totalPages} onclick={() => search(page + 1)}>Next ›</button>
      </div>
    </div>

    {#if selected}
      <form class="card item-form" onsubmit={tambahKeKeranjang}>
        <h3>{selected.nama}</h3>
        <div class="row">
          <div>
            <label for="qty">Jumlah</label>
            <input id="qty" type="number" min="1" bind:value={qty} bind:this={qtyInput} required />
          </div>
          <div>
            <label for="gudang">Gudang</label>
            <select id="gudang" bind:value={gudang}>
              {#each GUDANG as g (g)}
                <option value={g}>{g} — stok {selected[g]}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="diskon-mode">Diskon</label>
            <select id="diskon-mode" bind:value={diskonMode}>
              <option value="persen">% persen</option>
              <option value="nominal">Rp / unit</option>
            </select>
          </div>
          <div>
            <label for="diskon">{diskonMode === "persen" ? "Persen (0–100)" : "Rupiah per unit"}</label>
            <input id="diskon" type="number" min="0" bind:value={diskonValue} />
          </div>
          <button class="primary" type="submit">Tambah ➜</button>
        </div>
        <p class="muted preview">
          {angka(selected.hargaJual)} × {qty}
          {#if diskonValue > 0}
            − diskon = <b>
              {angka(
                selected.hargaJual * qty -
                  (diskonMode === "persen"
                    ? Math.round(selected.hargaJual * (diskonValue / 100)) * qty
                    : Math.round(diskonValue) * qty),
              )}
            </b>
          {:else}
            = <b>{angka(selected.hargaJual * qty)}</b>
          {/if}
        </p>
      </form>
    {/if}
  </section>

  <!-- kanan: keranjang + pembayaran -->
  <section class="right">
    <div class="card cart-card">
      <h3>Keranjang ({cart.count})</h3>
      <div class="cart-scroll">
        <table>
          <thead>
            <tr>
              <th>Produk</th>
              <th class="num">Qty</th>
              <th class="num">Diskon</th>
              <th class="num">Jumlah</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {#each cart.lines as l, i (i)}
              <tr>
                <td>
                  {l.nama}
                  <div class="muted small">{angka(l.hargaSatuan)} · {l.gudang}</div>
                </td>
                <td class="num qty-cell">
                  <input
                    type="number"
                    min="1"
                    value={l.qty}
                    onchange={(e) => cart.updateQty(i, Number(e.currentTarget.value))}
                  />
                </td>
                <td class="num">{angka(l.diskonTotal)}</td>
                <td class="num"><b>{angka(l.total)}</b></td>
                <td><button class="danger" onclick={() => cart.remove(i)}>✕</button></td>
              </tr>
            {:else}
              <tr><td colspan="5" class="empty">Belum ada item.</td></tr>
            {/each}
          </tbody>
        </table>
      </div>

      <div class="pay">
        <div class="total-line">
          <span>Total</span>
          <b>{rupiah(cart.total)}</b>
        </div>
        <div class="row">
          <div>
            <label for="tipe">Tipe pembeli</label>
            <input id="tipe" bind:value={tipePembeli} />
          </div>
          <div>
            <label for="bayar">Nominal bayar</label>
            <input id="bayar" type="number" min="0" bind:value={bayar} />
          </div>
        </div>
        <div class="total-line" class:minus={kembalian < 0}>
          <span>{kembalian >= 0 ? "Kembalian" : "Kurang"}</span>
          <b>{rupiah(Math.abs(kembalian))}</b>
        </div>
        <button class="primary big" disabled={saving || cart.count === 0} onclick={cetak}>
          {saving ? "Menyimpan…" : "🖨️ Simpan & Cetak Nota"}
        </button>
      </div>
    </div>
  </section>
</div>

<style>
  .layout {
    display: grid;
    grid-template-columns: minmax(420px, 1fr) minmax(380px, 480px);
    gap: 16px;
    align-items: start;
  }
  .left { display: flex; flex-direction: column; gap: 16px; }

  .search-bar { margin-bottom: 10px; }

  tr.selected { background: var(--primary-soft); }

  .item-form .row { align-items: end; }
  .item-form button.primary { flex: 0 0 auto; }
  .preview { margin: 10px 0 0; }

  .cart-card { position: sticky; top: 0; }
  .cart-scroll { max-height: 44vh; overflow-y: auto; }
  .qty-cell input { width: 64px; text-align: right; padding: 4px 6px; }
  .small { font-size: 12px; }

  .pay {
    border-top: 2px solid var(--border);
    margin-top: 12px;
    padding-top: 12px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .total-line {
    display: flex;
    justify-content: space-between;
    font-size: 16px;
  }
  .total-line.minus b { color: var(--danger); }
  button.big { padding: 12px; font-size: 15px; }
</style>
