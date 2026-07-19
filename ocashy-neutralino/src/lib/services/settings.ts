import { eq } from "drizzle-orm";
import { db, schema } from "../db/client";

const { settings } = schema;

/**
 * Properti print yang PERSISTEN — dulu bergantung ke print dialog browser
 * yang selalu reset. Sekarang ukuran kertas & orientasi dibakar langsung
 * ke dalam PDF dan disimpan di DB.
 */
export interface PrintSettings {
  paperSize: "A4" | "A5" | "Letter" | "Struk80";
  orientation: "portrait" | "landscape";
  marginMm: number;
  autoOpen: boolean; // buka PDF otomatis setelah dicetak
  silentPrint: boolean; // cetak langsung tanpa print dialog (via SumatraPDF)
  printerName: string; // nama printer untuk silent print (optional)
  sumatraPath: string; // lokasi SumatraPDF.exe (optional)
  namaToko: string;
  alamat: string;
  kontak: string;
  website: string;
  footer1: string;
  footer2: string;
}

export const DEFAULT_PRINT_SETTINGS: PrintSettings = {
  paperSize: "A5",
  orientation: "landscape",
  marginMm: 8,
  autoOpen: true,
  silentPrint: false,
  printerName: "",
  sumatraPath: "SumatraPDF.exe",
  namaToko: "Istana Keramik",
  alamat:
    "Jl. WR Supratman No.24, Baledono, Kec. Purworejo, Kabupaten Purworejo, Jawa Tengah 54118",
  kontak: "Telp: (0275) 321 597 | WA: 087714141252 | IG: @istanakeramik_pwr",
  website: "https://istanakeramik.com",
  footer1: "*Mohon barang diperiksa dulu sebelum meninggalkan toko.",
  footer2: "**Barang yang sudah dibeli tidak dapat ditukar kembali.",
};

const PRINT_KEY = "print_settings";

export async function getPrintSettings(): Promise<PrintSettings> {
  const rows = await db.select().from(settings).where(eq(settings.key, PRINT_KEY)).limit(1);
  if (!rows[0]) return { ...DEFAULT_PRINT_SETTINGS };
  try {
    return { ...DEFAULT_PRINT_SETTINGS, ...JSON.parse(rows[0].value) };
  } catch {
    return { ...DEFAULT_PRINT_SETTINGS };
  }
}

export async function savePrintSettings(value: PrintSettings): Promise<void> {
  const json = JSON.stringify(value);
  await db
    .insert(settings)
    .values({ key: PRINT_KEY, value: json })
    .onConflictDoUpdate({ target: settings.key, set: { value: json } });
}
