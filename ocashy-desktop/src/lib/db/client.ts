import Database from "@tauri-apps/plugin-sql";
import { drizzle } from "drizzle-orm/sqlite-proxy";
import * as schema from "./schema";

/**
 * Drizzle ORM di atas tauri-plugin-sql (SQLite).
 *
 * Kenapa sqlite-proxy: webview tidak bisa buka file SQLite langsung, jadi
 * query yang dibangun Drizzle dikirim ke sisi Rust lewat plugin-sql.
 * Skema Drizzle sendiri portable — pindah ke Turso/Postgres nanti cukup
 * ganti driver + dialect, service layer tidak berubah.
 */

let sqlite: Database | null = null;

export async function getSqlite(): Promise<Database> {
  if (!sqlite) {
    // Migrasi (folder /drizzle) dijalankan otomatis oleh sisi Rust saat load.
    sqlite = await Database.load("sqlite:ocashy.db");
  }
  return sqlite;
}

function isSelect(sql: string): boolean {
  const s = sql.trimStart().toLowerCase();
  return s.startsWith("select") || s.startsWith("pragma") || s.startsWith("with");
}

export const db = drizzle<typeof schema>(
  async (sql, params, method) => {
    const dbi = await getSqlite();

    if (!isSelect(sql)) {
      // INSERT/UPDATE/DELETE. Drizzle kadang minta hasil RETURNING;
      // plugin-sql execute tidak mengembalikan rows, jadi hindari
      // .returning() di service layer.
      await dbi.execute(sql, params as unknown[]);
      return { rows: [] };
    }

    // plugin-sql mengembalikan array objek; drizzle sqlite-proxy butuh
    // array-of-arrays sesuai urutan kolom SELECT.
    const rows = await dbi.select<Record<string, unknown>[]>(sql, params as unknown[]);
    const values = rows.map((row) => Object.values(row));
    return { rows: method === "get" ? (values[0] ?? []) : values };
  },
  { schema },
);

export { schema };
