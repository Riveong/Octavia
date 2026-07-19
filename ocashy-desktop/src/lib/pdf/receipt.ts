import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import { mkdir, writeFile, exists } from "@tauri-apps/plugin-fs";
import { BaseDirectory, appDataDir, join } from "@tauri-apps/api/path";
import { openPath } from "@tauri-apps/plugin-opener";
import { invoke } from "@tauri-apps/api/core";
import type { NotaLengkap } from "../services/nota";
import type { PrintSettings } from "../services/settings";
import { angka, tanggal } from "../utils/format";

// Ukuran kertas dalam mm (portrait). "Struk80" = roll thermal 80mm,
// tinggi dinamis mengikuti isi.
const PAPER_MM: Record<PrintSettings["paperSize"], [number, number]> = {
  A4: [210, 297],
  A5: [148, 210],
  Letter: [215.9, 279.4],
  Struk80: [80, 297],
};

function buildDoc(data: NotaLengkap, s: PrintSettings): jsPDF {
  const isStruk = s.paperSize === "Struk80";
  const [w, h] = PAPER_MM[s.paperSize];
  const orientation = isStruk ? "portrait" : s.orientation;

  const doc = new jsPDF({
    orientation,
    unit: "mm",
    format: isStruk ? [w, h] : s.paperSize.toLowerCase(),
  });

  const pageW = doc.internal.pageSize.getWidth();
  const m = Math.max(2, s.marginMm);
  let y = m + 2;

  const base = isStruk ? 7 : 9;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(base + 3);
  doc.text(s.namaToko, m, y);
  y += isStruk ? 3.5 : 4.5;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(base - 2);
  const headerLines: string[] = [
    `Nota Penjualan ${data.nota.tipePembeli}`,
    ...doc.splitTextToSize(s.alamat, pageW - m * 2),
    ...doc.splitTextToSize(s.kontak, pageW - m * 2),
    s.website,
    `No. Faktur: ${data.nota.nomorFaktur}   Waktu: ${tanggal(data.nota.waktu)}`,
  ].filter(Boolean);
  for (const line of headerLines) {
    doc.text(line, m, y);
    y += isStruk ? 2.8 : 3.4;
  }
  y += 2;

  const body = data.items.map((it, i) => [
    String(i + 1),
    it.nama,
    angka(it.hargaSatuan),
    angka(it.qty),
    angka(it.diskonSatuan),
    angka(it.diskonTotal),
    it.gudang,
    angka(it.total),
  ]);

  const foot: string[][] = [
    ["", "", "", "", "", "", "Total", angka(data.nota.total)],
    ["", "", "", "", "", "", "Bayar", angka(data.nota.bayar)],
    [
      "",
      "",
      "",
      "",
      "",
      "",
      data.nota.kembalian >= 0 ? "Kembalian" : "Kurang",
      angka(Math.abs(data.nota.kembalian)),
    ],
  ];

  autoTable(doc, {
    startY: y,
    margin: { left: m, right: m, top: m, bottom: m + 8 },
    head: [["No", "Produk", "Harga", "QTY", "Disk/Sat", "Disk Total", "Gudang", "Jumlah"]],
    body,
    foot,
    styles: {
      fontSize: isStruk ? 6 : 8,
      cellPadding: isStruk ? 0.6 : 1.2,
      lineColor: [30, 30, 30],
      lineWidth: 0.15,
      textColor: [20, 20, 20],
    },
    headStyles: { fillColor: [240, 240, 240], textColor: [20, 20, 20], fontStyle: "bold" },
    footStyles: { fillColor: [255, 255, 255], textColor: [20, 20, 20], fontStyle: "bold" },
    columnStyles: {
      0: { cellWidth: isStruk ? 5 : 8 },
      2: { halign: "right" },
      3: { halign: "right" },
      4: { halign: "right" },
      5: { halign: "right" },
      7: { halign: "right" },
    },
    theme: "grid",
  });

  const endY = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY;
  doc.setFontSize(base - 2.5);
  doc.setFont("helvetica", "italic");
  doc.text(s.footer1, m, endY + 4);
  doc.text(s.footer2, m, endY + 7.5);
  doc.setFont("helvetica", "normal");
  doc.text("CATATAN TAMBAHAN:", m, endY + 12);

  return doc;
}

/**
 * Buat PDF nota sesuai properti print tersimpan, simpan ke
 * %APPDATA%/<app>/receipts/, lalu (opsional) buka dengan viewer default
 * atau cetak langsung menggunakan SumatraPDF.
 */
export async function cetakNota(data: NotaLengkap, s: PrintSettings): Promise<string> {
  const doc = buildDoc(data, s);
  const bytes = new Uint8Array(doc.output("arraybuffer"));

  const dir = "receipts";
  if (!(await exists(dir, { baseDir: BaseDirectory.AppData }))) {
    await mkdir(dir, { baseDir: BaseDirectory.AppData, recursive: true });
  }
  const fileName = `nota-${data.nota.nomorFaktur}.pdf`;
  const rel = `${dir}/${fileName}`;
  await writeFile(rel, bytes, { baseDir: BaseDirectory.AppData });

  const fullPath = await join(await appDataDir(), dir, fileName);

  if (s.silentPrint) {
    try {
      await invoke("print_pdf_via_sumatra", {
        pdfPath: fullPath,
        printerName: s.printerName || null,
        sumatraPath: s.sumatraPath || null,
      });
    } catch (e) {
      throw new Error(`Direct print failed: ${e}`);
    }
  }

  if (s.autoOpen) {
    await openPath(fullPath);
  }
  return fullPath;
}
