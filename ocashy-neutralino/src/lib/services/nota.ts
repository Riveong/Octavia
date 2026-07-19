import { desc, eq, like, sql } from "drizzle-orm";
import { db, schema } from "../db/client";
import type { Nota, NotaItem } from "../db/schema";
import { kurangiStok, GUDANG, type Gudang } from "./produk";

const { nota, notaItem } = schema;

export interface CartLine {
  idBarang: string | null;
  nama: string;
  hargaSatuan: number;
  qty: number;
  diskonSatuan: number; // potongan per unit (rupiah)
  diskonTotal: number; // total potongan baris
  gudang: string;
  total: number; // harga akhir baris
}

export interface NotaBaru {
  tipePembeli: string;
  bayar: number;
  lines: CartLine[];
}

export interface NotaLengkap {
  nota: Nota;
  items: NotaItem[];
}

function buatNomorFaktur(d: Date): string {
  const p = (n: number, w = 2) => String(n).padStart(w, "0");
  return (
    `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}` +
    `-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}` +
    `-${p(Math.floor(Math.random() * 1000), 3)}`
  );
}

/** Simpan nota + item, lalu kurangi stok gudang terkait. */
export async function simpanNota(data: NotaBaru): Promise<NotaLengkap> {
  if (data.lines.length === 0) throw new Error("Keranjang masih kosong.");

  const now = new Date();
  const total = data.lines.reduce((s, l) => s + l.total, 0);
  const nomorFaktur = buatNomorFaktur(now);

  await db.insert(nota).values({
    nomorFaktur,
    waktu: now.toISOString(),
    tipePembeli: data.tipePembeli || "Umum",
    total,
    bayar: data.bayar,
    kembalian: data.bayar - total,
  });

  const saved = await db
    .select()
    .from(nota)
    .where(eq(nota.nomorFaktur, nomorFaktur))
    .limit(1);
  const header = saved[0];
  if (!header) throw new Error("Gagal menyimpan nota.");

  for (const l of data.lines) {
    await db.insert(notaItem).values({
      notaId: header.id,
      idBarang: l.idBarang,
      nama: l.nama,
      hargaSatuan: l.hargaSatuan,
      qty: l.qty,
      diskonSatuan: l.diskonSatuan,
      diskonTotal: l.diskonTotal,
      gudang: l.gudang,
      total: l.total,
    });
    if (l.idBarang && (GUDANG as readonly string[]).includes(l.gudang)) {
      await kurangiStok(l.idBarang, l.gudang as Gudang, l.qty);
    }
  }

  const items = await db.select().from(notaItem).where(eq(notaItem.notaId, header.id));
  return { nota: header, items };
}

export interface PagedNota {
  items: Nota[];
  total: number;
  totalPages: number;
  page: number;
}

export async function daftarNota(q = "", page = 1, limit = 15): Promise<PagedNota> {
  const where = q.trim() ? like(nota.nomorFaktur, `%${q.trim()}%`) : undefined;

  const [{ count }] = await db
    .select({ count: sql<number>`count(*)` })
    .from(nota)
    .where(where);

  const items = await db
    .select()
    .from(nota)
    .where(where)
    .orderBy(desc(nota.waktu))
    .limit(limit)
    .offset((page - 1) * limit);

  return { items, total: count, totalPages: Math.max(1, Math.ceil(count / limit)), page };
}

export async function ambilNota(id: number): Promise<NotaLengkap | undefined> {
  const headers = await db.select().from(nota).where(eq(nota.id, id)).limit(1);
  if (!headers[0]) return undefined;
  const items = await db.select().from(notaItem).where(eq(notaItem.notaId, id));
  return { nota: headers[0], items };
}

export async function hapusNota(id: number): Promise<void> {
  await db.delete(notaItem).where(eq(notaItem.notaId, id));
  await db.delete(nota).where(eq(nota.id, id));
}
