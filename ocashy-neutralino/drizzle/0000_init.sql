CREATE TABLE IF NOT EXISTS `barang` (
	`id_barang` text PRIMARY KEY NOT NULL,
	`nama` text NOT NULL,
	`harga_jual` integer NOT NULL DEFAULT 0,
	`harga_beli` integer NOT NULL DEFAULT 0,
	`id_kategori` text NOT NULL DEFAULT '',
	`kulon` integer NOT NULL DEFAULT 0,
	`toko` integer NOT NULL DEFAULT 0,
	`pink` integer NOT NULL DEFAULT 0,
	`wetan` integer NOT NULL DEFAULT 0,
	`kedungsari` integer NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS `idx_barang_nama` ON `barang` (`nama`);

CREATE TABLE IF NOT EXISTS `nota` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`nomor_faktur` text NOT NULL UNIQUE,
	`waktu` text NOT NULL,
	`tipe_pembeli` text NOT NULL DEFAULT 'Umum',
	`total` real NOT NULL DEFAULT 0,
	`bayar` real NOT NULL DEFAULT 0,
	`kembalian` real NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS `idx_nota_waktu` ON `nota` (`waktu`);

CREATE TABLE IF NOT EXISTS `nota_item` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`nota_id` integer NOT NULL REFERENCES `nota`(`id`) ON DELETE CASCADE,
	`id_barang` text,
	`nama` text NOT NULL,
	`harga_satuan` real NOT NULL DEFAULT 0,
	`qty` real NOT NULL DEFAULT 1,
	`diskon_satuan` real NOT NULL DEFAULT 0,
	`diskon_total` real NOT NULL DEFAULT 0,
	`gudang` text NOT NULL DEFAULT '',
	`total` real NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS `idx_nota_item_nota` ON `nota_item` (`nota_id`);

CREATE TABLE IF NOT EXISTS `settings` (
	`key` text PRIMARY KEY NOT NULL,
	`value` text NOT NULL
);
