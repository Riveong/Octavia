<script lang="ts">
  import { onMount } from "svelte";
  import { open, save } from "@tauri-apps/plugin-dialog";
  import { readTextFile, writeTextFile } from "@tauri-apps/plugin-fs";
  import {
    getPrintSettings,
    savePrintSettings,
    DEFAULT_PRINT_SETTINGS,
    type PrintSettings,
  } from "../lib/services/settings";
  import { semuaBarang, importBarang } from "../lib/services/produk";
  import { toast } from "../lib/stores/toast.svelte";
  import type { NewBarang } from "../lib/db/schema";

  let s = $state<PrintSettings>({ ...DEFAULT_PRINT_SETTINGS });
  let loaded = $state(false);
  let busy = $state(false);

  onMount(() => {
    getPrintSettings()
      .then((v) => {
        s = v;
        loaded = true;
      })
      .catch((e) => toast.error(`Gagal memuat pengaturan: ${e}`));
  });

  async function simpan(e: SubmitEvent) {
    e.preventDefault();
    try {
      await savePrintSettings($state.snapshot(s));
      toast.success("Properti print tersimpan — dipakai untuk semua nota berikutnya.");
    } catch (err) {
      toast.error(`Gagal menyimpan: ${err}`);
    }
  }

  // --- ekspor / impor data ---
  async function eksporJson() {
    busy = true;
    try {
      const rows = await semuaBarang();
      const path = await save({
        title: "Ekspor data produk",
        defaultPath: `ocashy-produk-${new Date().toISOString().slice(0, 10)}.json`,
        filters: [{ name: "JSON", extensions: ["json"] }],
      });
      if (!path) return;
      await writeTextFile(path, JSON.stringify(rows, null, 2));
      toast.success(`${rows.length} produk diekspor ke ${path}`);
    } catch (e) {
      toast.error(`Gagal ekspor: ${e}`);
    } finally {
      busy = false;
    }
  }

  async function imporJson() {
    busy = true;
    try {
      const path = await open({
        title: "Impor data produk (JSON)",
        multiple: false,
        filters: [{ name: "JSON", extensions: ["json"] }],
      });
      if (!path || Array.isArray(path)) return;
      const text = await readTextFile(path);
      const rows = JSON.parse(text) as NewBarang[];
      if (!Array.isArray(rows)) throw new Error("Format file tidak valid (harus array JSON).");
      const n = await importBarang(rows);
      toast.success(`${n} produk diimpor/diperbarui.`);
    } catch (e) {
      toast.error(`Gagal impor: ${e}`);
    } finally {
      busy = false;
    }
  }
</script>

<h2>Pengaturan</h2>

<div class="stack">
  <form class="card" onsubmit={simpan}>
    <h3>🖨️ Properti Print (tersimpan permanen)</h3>
    <p class="muted">
      Ukuran kertas & orientasi dibakar langsung ke file PDF nota — tidak lagi
      tergantung pengaturan print browser yang sering reset.
    </p>

    {#if loaded}
      <div class="grid">
        <div>
          <label for="paper">Ukuran kertas</label>
          <select id="paper" bind:value={s.paperSize}>
            <option value="A4">A4 (210 × 297 mm)</option>
            <option value="A5">A5 (148 × 210 mm)</option>
            <option value="Letter">Letter (216 × 279 mm)</option>
            <option value="Struk80">Struk thermal 80 mm</option>
          </select>
        </div>
        <div>
          <label for="orient">Orientasi</label>
          <select id="orient" bind:value={s.orientation} disabled={s.paperSize === "Struk80"}>
            <option value="landscape">Landscape</option>
            <option value="portrait">Portrait</option>
          </select>
        </div>
        <div>
          <label for="margin">Margin (mm)</label>
          <input id="margin" type="number" min="2" max="30" bind:value={s.marginMm} />
        </div>
        <div class="check">
          <label for="autoopen">
            <input id="autoopen" type="checkbox" bind:checked={s.autoOpen} />
            Buka PDF otomatis setelah cetak
          </label>
        </div>
      </div>

      <h3 class="sub">Kop Nota</h3>
      <div class="grid">
        <div><label for="toko">Nama toko</label><input id="toko" bind:value={s.namaToko} /></div>
        <div class="wide"><label for="alamat">Alamat</label><input id="alamat" bind:value={s.alamat} /></div>
        <div class="wide"><label for="kontak">Kontak</label><input id="kontak" bind:value={s.kontak} /></div>
        <div><label for="web">Website</label><input id="web" bind:value={s.website} /></div>
        <div class="wide"><label for="f1">Catatan kaki 1</label><input id="f1" bind:value={s.footer1} /></div>
        <div class="wide"><label for="f2">Catatan kaki 2</label><input id="f2" bind:value={s.footer2} /></div>
      </div>

      <div class="actions">
        <button type="button" onclick={() => (s = { ...DEFAULT_PRINT_SETTINGS })}>Reset default</button>
        <button class="primary" type="submit">Simpan Pengaturan</button>
      </div>
    {:else}
      <p class="muted">Memuat…</p>
    {/if}
  </form>

  <div class="card">
    <h3>💾 Data</h3>
    <p class="muted">
      Impor menerima file JSON hasil <code>npm run export:mariadb</code> (migrasi dari
      MariaDB/XAMPP lama) maupun hasil ekspor dari aplikasi ini (backup/pindah PC).
    </p>
    <div class="btns">
      <button disabled={busy} onclick={imporJson}>📥 Impor produk (JSON)</button>
      <button disabled={busy} onclick={eksporJson}>📤 Ekspor produk (JSON)</button>
    </div>
  </div>
</div>

<style>
  .stack {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 860px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }
  .wide { grid-column: span 3; }
  .sub { margin-top: 16px; }
  .check { display: flex; align-items: end; }
  .check label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    color: var(--text);
    margin: 0;
  }
  .check input { width: auto; }
  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 14px;
  }
  .btns { display: flex; gap: 10px; }
  code {
    background: var(--bg);
    padding: 1px 6px;
    border-radius: 5px;
    font-size: 12.5px;
  }
</style>
