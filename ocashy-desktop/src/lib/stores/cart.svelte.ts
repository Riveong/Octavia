import type { CartLine } from "../services/nota";
import type { Barang } from "../db/schema";

export type DiskonMode = "persen" | "nominal";

/** Keranjang kasir — state murni Svelte 5 runes, tanpa manipulasi DOM. */
class Cart {
  lines = $state<CartLine[]>([]);

  total = $derived(this.lines.reduce((s, l) => s + l.total, 0));
  count = $derived(this.lines.length);

  add(
    b: Barang,
    qty: number,
    gudang: string,
    diskonMode: DiskonMode,
    diskonValue: number,
  ): void {
    const hargaSatuan = b.hargaJual;
    const bruto = hargaSatuan * qty;

    let diskonSatuan = 0;
    if (diskonMode === "persen") {
      diskonSatuan = Math.round(hargaSatuan * (diskonValue / 100));
    } else {
      diskonSatuan = Math.round(diskonValue);
    }
    const diskonTotal = diskonSatuan * qty;

    this.lines.push({
      idBarang: b.idBarang,
      nama: b.nama,
      hargaSatuan,
      qty,
      diskonSatuan,
      diskonTotal,
      gudang,
      total: bruto - diskonTotal,
    });
  }

  updateQty(index: number, qty: number): void {
    const l = this.lines[index];
    if (!l || qty < 1) return;
    l.qty = qty;
    l.diskonTotal = l.diskonSatuan * qty;
    l.total = l.hargaSatuan * qty - l.diskonTotal;
  }

  remove(index: number): void {
    this.lines.splice(index, 1);
  }

  clear(): void {
    this.lines = [];
  }
}

export const cart = new Cart();
