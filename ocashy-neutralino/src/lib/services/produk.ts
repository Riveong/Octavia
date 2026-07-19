import { and, asc, eq, like, sql } from "drizzle-orm";
import { db, schema } from "../db/client";
import type { Barang, NewBarang } from "../db/schema";

const { barang } = schema;

export const GUDANG = ["kulon", "toko", "pink", "wetan", "kedungsari"] as const;
export type Gudang = (typeof GUDANG)[number];

export function totalStok(b: Barang): number {
  return b.kulon + b.toko + b.pink + b.wetan + b.kedungsari;
}

export interface PagedBarang {
  items: Barang[];
  total: number;
  totalPages: number;
  page: number;
}

export async function cariBarang(
  q: string,
  page = 1,
  limit = 12,
): Promise<PagedBarang> {
  const pattern = `%${q.trim()}%`;
  const where = q.trim() ? like(barang.nama, pattern) : undefined;

  const [{ count }] = await db
    .select({ count: sql<number>`count(*)` })
    .from(barang)
    .where(where);

  const items = await db
    .select()
    .from(barang)
    .where(where)
    .orderBy(asc(barang.nama))
    .limit(limit)
    .offset((page - 1) * limit);

  return {
    items,
    total: count,
    totalPages: Math.max(1, Math.ceil(count / limit)),
    page,
  };
}

export async function getBarang(idBarang: string): Promise<Barang | undefined> {
  const rows = await db.select().from(barang).where(eq(barang.idBarang, idBarang)).limit(1);
  return rows[0];
}

export async function tambahBarang(data: NewBarang): Promise<void> {
  const existing = await getBarang(data.idBarang);
  if (existing) throw new Error(`ID barang "${data.idBarang}" sudah dipakai.`);
  await db.insert(barang).values(data);
}

export async function ubahBarang(idBarang: string, data: Partial<NewBarang>): Promise<void> {
  await db.update(barang).set(data).where(eq(barang.idBarang, idBarang));
}

export async function hapusBarang(idBarang: string): Promise<void> {
  await db.delete(barang).where(eq(barang.idBarang, idBarang));
}

/** Kurangi stok gudang setelah penjualan (tidak sampai minus). */
export async function kurangiStok(idBarang: string, gudang: Gudang, qty: number): Promise<void> {
  const col = barang[gudang];
  await db
    .update(barang)
    .set({ [gudang]: sql`max(0, ${col} - ${qty})` })
    .where(eq(barang.idBarang, idBarang));
}

export async function semuaBarang(): Promise<Barang[]> {
  return db.select().from(barang).orderBy(asc(barang.nama));
}

/** Import massal (dari export MariaDB / backup JSON). Replace berdasarkan id. */
export async function importBarang(rows: NewBarang[]): Promise<number> {
  let n = 0;
  for (const row of rows) {
    await db
      .insert(barang)
      .values(row)
      .onConflictDoUpdate({ target: barang.idBarang, set: row });
    n++;
  }
  return n;
}
