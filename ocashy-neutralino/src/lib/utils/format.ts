/** Format angka jadi "12.345" gaya Indonesia (tanpa simbol). */
export function angka(n: number): string {
  return new Intl.NumberFormat("id-ID", { maximumFractionDigits: 0 }).format(n);
}

/** Format rupiah "Rp 12.345". */
export function rupiah(n: number): string {
  return `Rp ${angka(n)}`;
}

export function tanggal(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
