# Ocashy Desktop v2

Rewrite penuh dari app kasir lama (FastAPI + Svelte 3 + MariaDB/XAMPP + `.bat`)
menjadi **satu aplikasi desktop**: Tauri 2 + Svelte 5 + SQLite (Drizzle ORM).

Tidak ada lagi XAMPP, uvicorn, `.bat`, atau browser — satu installer `.exe`,
database tertanam di dalam aplikasi.

## Fitur

- **Kasir** — cari produk realtime, keranjang dengan edit qty, diskon persen/nominal
  per item, hitung kembalian, simpan + cetak sekali klik. Stok gudang otomatis
  berkurang saat penjualan.
- **Produk** — CRUD lengkap dengan stok per gudang (kulon/toko/pink/wetan/kedungsari).
- **Riwayat Nota** — semua nota tercatat di database (bukan cuma file PDF), bisa
  dilihat detailnya dan **dicetak ulang** kapan saja.
- **Properti print tersimpan** — ukuran kertas (A4/A5/Letter/struk 80mm),
  orientasi, margin, dan kop nota disimpan permanen di DB dan **dibakar langsung
  ke PDF**, jadi tidak tergantung setting print browser yang sering reset.
- **Impor/Ekspor** — migrasi data dari MariaDB lama, backup/restore JSON.

## Setup mesin development (sekali saja)

1. **Node.js 20+** — https://nodejs.org
2. **Rust** — https://rustup.rs (jalankan `rustup-init.exe`, pilih default)
3. **Visual Studio Build Tools** (perlu admin) —
   https://aka.ms/vs/17/release/vs_BuildTools.exe
   → centang workload **"Desktop development with C++"** (termasuk Windows SDK).
4. **WebView2** — biasanya sudah ada di Windows 10/11 (bawaan Edge).

Lalu:

```sh
cd ocashy-desktop
npm install
npm run tauri dev     # jalankan mode development
npm run tauri build   # build installer .exe (hasil di src-tauri/target/release/bundle/nsis)
```

> Ikon: sebelum `tauri build` pertama, generate ikon dari logo toko:
> `npm run tauri icon path/ke/logo.png` (butuh PNG persegi min. 512×512).

## Migrasi data dari MariaDB (XAMPP) lama

Di PC yang masih punya XAMPP dengan database lama:

```sh
cd ocashy-desktop
set DB_HOST=localhost
set DB_USER=root
set DB_PASS=
set DB_NAME=nama_database_lama
npm run export:mariadb
```

Hasilnya `scripts/ocashy-produk-export.json`. Buka aplikasi Ocashy →
**Pengaturan → Impor produk (JSON)** → pilih file itu. Selesai — data lama masuk,
MariaDB tidak disentuh (tetap aman sebagai backup).

## Arsitektur

```
src/
  lib/db/        schema.ts (Drizzle) + client.ts (proxy ke tauri-plugin-sql)
  lib/services/  produk.ts, nota.ts, settings.ts — semua query lewat Drizzle
  lib/pdf/       receipt.ts — jsPDF, properti print dari DB
  lib/stores/    cart & toast (Svelte 5 runes)
  pages/         Kasir, Produk, Riwayat, Pengaturan
src-tauri/       Rust shell + registrasi migrasi SQL
drizzle/         file migrasi SQL (dijalankan otomatis saat app start)
scripts/         export-mariadb.mjs (migrasi one-time)
```

- **Database**: SQLite, file `ocashy.db` di `%APPDATA%\com.istanakeramik.ocashy\`.
  Backup = copy satu file itu.
- **Ganti database nanti** (Turso/Postgres): skema Drizzle portable — ganti
  driver di `src/lib/db/client.ts` + dialect di `drizzle.config.ts`;
  service layer tidak berubah.
- **Migrasi skema baru**: ubah `src/lib/db/schema.ts`, jalankan
  `npm run db:generate`, daftarkan file SQL baru di `src-tauri/src/lib.rs`.
- **PDF nota** tersimpan di `%APPDATA%\com.istanakeramik.ocashy\receipts\`.
