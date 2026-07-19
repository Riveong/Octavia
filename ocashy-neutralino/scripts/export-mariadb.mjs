/**
 * Ekspor tabel `barang` dari MariaDB (XAMPP) lama ke JSON yang bisa
 * diimpor lewat menu Pengaturan → Impor produk di aplikasi Ocashy Desktop.
 *
 * Jalankan di PC yang masih punya XAMPP dengan database lama:
 *
 *   set DB_HOST=localhost
 *   set DB_USER=root
 *   set DB_PASS=
 *   set DB_NAME=<nama-database-lama>
 *   npm run export:mariadb
 *
 * Hasil: ocashy-produk-export.json di folder ini.
 */
import { createConnection } from "mysql2/promise";
import { writeFile } from "node:fs/promises";

const cfg = {
  host: process.env.DB_HOST ?? "localhost",
  user: process.env.DB_USER ?? "root",
  password: process.env.DB_PASS ?? "",
  database: process.env.DB_NAME,
};

if (!cfg.database) {
  console.error("Set dulu env DB_NAME (nama database lama di XAMPP).");
  process.exit(1);
}

const conn = await createConnection(cfg);
const [rows] = await conn.query("SELECT * FROM barang");
await conn.end();

// Kolom MariaDB lama -> field aplikasi baru.
const mapped = rows.map((r) => ({
  idBarang: String(r.Id_barang ?? r.id_barang ?? ""),
  nama: String(r.Nama ?? r.nama ?? ""),
  hargaJual: Number(r.HargaJual ?? r.hargaJual ?? 0),
  hargaBeli: Number(r.HargaBeli ?? r.hargaBeli ?? 0),
  idKategori: String(r.Id_kategori ?? r.id_kategori ?? ""),
  kulon: Number(r.Kulon ?? r.kulon ?? 0),
  toko: Number(r.Toko ?? r.toko ?? 0),
  pink: Number(r.Pink ?? r.pink ?? 0),
  wetan: Number(r.Wetan ?? r.wetan ?? 0),
  kedungsari: Number(r.Kedungsari ?? r.kedungsari ?? 0),
}));

const bad = mapped.filter((m) => !m.idBarang || !m.nama);
if (bad.length) {
  console.warn(`Peringatan: ${bad.length} baris tanpa id/nama dilewati.`);
}
const good = mapped.filter((m) => m.idBarang && m.nama);

const out = new URL("./ocashy-produk-export.json", import.meta.url);
await writeFile(out, JSON.stringify(good, null, 2));
console.log(`OK: ${good.length} produk diekspor ke ${out.pathname}`);
console.log("Buka aplikasi Ocashy → Pengaturan → Impor produk (JSON).");
