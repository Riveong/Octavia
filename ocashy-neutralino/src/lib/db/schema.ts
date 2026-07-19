import { sqliteTable, text, integer, real, index } from "drizzle-orm/sqlite-core";

// Master produk. Kolom gudang mengikuti data lama (kulon/toko/pink/wetan/kedungsari)
// supaya migrasi dari MariaDB 1:1.
export const barang = sqliteTable(
  "barang",
  {
    idBarang: text("id_barang").primaryKey(),
    nama: text("nama").notNull(),
    hargaJual: integer("harga_jual").notNull().default(0),
    hargaBeli: integer("harga_beli").notNull().default(0),
    idKategori: text("id_kategori").notNull().default(""),
    kulon: integer("kulon").notNull().default(0),
    toko: integer("toko").notNull().default(0),
    pink: integer("pink").notNull().default(0),
    wetan: integer("wetan").notNull().default(0),
    kedungsari: integer("kedungsari").notNull().default(0),
  },
  (t) => [index("idx_barang_nama").on(t.nama)],
);

// Header nota penjualan — sebelumnya nota cuma jadi file PDF, sekarang tercatat di DB.
export const nota = sqliteTable(
  "nota",
  {
    id: integer("id").primaryKey({ autoIncrement: true }),
    nomorFaktur: text("nomor_faktur").notNull().unique(),
    waktu: text("waktu").notNull(), // ISO 8601
    tipePembeli: text("tipe_pembeli").notNull().default("Umum"),
    total: real("total").notNull().default(0),
    bayar: real("bayar").notNull().default(0),
    kembalian: real("kembalian").notNull().default(0),
  },
  (t) => [index("idx_nota_waktu").on(t.waktu)],
);

export const notaItem = sqliteTable(
  "nota_item",
  {
    id: integer("id").primaryKey({ autoIncrement: true }),
    notaId: integer("nota_id")
      .notNull()
      .references(() => nota.id, { onDelete: "cascade" }),
    idBarang: text("id_barang"),
    nama: text("nama").notNull(),
    hargaSatuan: real("harga_satuan").notNull().default(0),
    qty: real("qty").notNull().default(1),
    diskonSatuan: real("diskon_satuan").notNull().default(0),
    diskonTotal: real("diskon_total").notNull().default(0),
    gudang: text("gudang").notNull().default(""),
    total: real("total").notNull().default(0),
  },
  (t) => [index("idx_nota_item_nota").on(t.notaId)],
);

// Key-value settings (properti print, dsb.) — persisten antar sesi.
export const settings = sqliteTable("settings", {
  key: text("key").primaryKey(),
  value: text("value").notNull(),
});

export type Barang = typeof barang.$inferSelect;
export type NewBarang = typeof barang.$inferInsert;
export type Nota = typeof nota.$inferSelect;
export type NotaItem = typeof notaItem.$inferSelect;
export type NewNotaItem = typeof notaItem.$inferInsert;
