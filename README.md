# Octavia / Ocashy

Aplikasi kasir (POS) Istana Keramik.

| Folder | Status | Isi |
| --- | --- | --- |
| **`ocashy-desktop/`** | ✅ **Aktif — pakai ini** | Rewrite v2: aplikasi desktop Tauri 2 + Svelte 5 + SQLite (Drizzle ORM). Satu installer `.exe`, tanpa XAMPP/uvicorn/browser. Lihat [ocashy-desktop/README.md](ocashy-desktop/README.md) untuk setup & migrasi data. |
| `ocashy/` | 🗄️ Legacy | App lama: FastAPI + Svelte 3 + MariaDB (XAMPP), dijalankan lewat `Ocashy start.bat`. Disimpan hanya sebagai referensi & sumber migrasi data. |

Migrasi data dari MariaDB lama → app baru: jalankan `npm run export:mariadb`
di `ocashy-desktop/` (lihat README di sana), lalu impor JSON-nya lewat menu
**Pengaturan** di aplikasi.
