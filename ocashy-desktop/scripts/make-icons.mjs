/**
 * Generate ikon placeholder Ocashy (lingkaran biru + ring "O" putih) tanpa
 * dependency apa pun — murni Node built-in (zlib). Dipakai supaya
 * `tauri build` langsung jalan; ganti kapan saja dengan logo asli via
 * `npm run tauri icon logo.png`.
 *
 * Jalankan:  node scripts/make-icons.mjs
 */
import { deflateSync } from "node:zlib";
import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "src-tauri", "icons");
mkdirSync(OUT, { recursive: true });

// ---- CRC32 (untuk chunk PNG) ----
const CRC_TABLE = new Int32Array(256).map((_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c;
});
function crc32(buf) {
  let c = -1;
  for (const b of buf) c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ -1) >>> 0;
}

function chunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length);
  const body = Buffer.concat([Buffer.from(type, "ascii"), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(body));
  return Buffer.concat([len, body, crc]);
}

/** Render ikon size×size RGBA: lingkaran biru #2563eb + ring putih. */
function renderRGBA(size) {
  const px = Buffer.alloc(size * size * 4);
  const c = (size - 1) / 2;
  const R = size * 0.48; // lingkaran luar
  const r1 = size * 0.30; // ring luar
  const r2 = size * 0.18; // ring dalam
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const d = Math.hypot(x - c, y - c);
      const i = (y * size + x) * 4;
      if (d <= R) {
        const white = d <= r1 && d >= r2;
        px[i] = white ? 255 : 0x25;
        px[i + 1] = white ? 255 : 0x63;
        px[i + 2] = white ? 255 : 0xeb;
        // anti-alias tepi luar sederhana
        px[i + 3] = d > R - 1 ? Math.round(255 * (R - d)) : 255;
      }
    }
  }
  return px;
}

function encodePNG(size) {
  const rgba = renderRGBA(size);
  // tiap scanline diawali filter byte 0
  const raw = Buffer.alloc(size * (size * 4 + 1));
  for (let y = 0; y < size; y++) {
    rgba.copy(raw, y * (size * 4 + 1) + 1, y * size * 4, (y + 1) * size * 4);
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0);
  ihdr.writeUInt32BE(size, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // color type RGBA
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk("IHDR", ihdr),
    chunk("IDAT", deflateSync(raw)),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

// PNG yang dibutuhkan tauri.conf.json
const pngs = {
  "32x32.png": 32,
  "128x128.png": 128,
  "128x128@2x.png": 256,
  "icon.png": 512,
};
for (const [name, size] of Object.entries(pngs)) {
  writeFileSync(join(OUT, name), encodePNG(size));
}

// icon.ico — kontainer ICO berisi PNG (didukung Windows Vista+)
const icoSizes = [16, 32, 48, 256];
const blobs = icoSizes.map((s) => encodePNG(s));
const header = Buffer.alloc(6);
header.writeUInt16LE(1, 2); // type: icon
header.writeUInt16LE(icoSizes.length, 4);
let offset = 6 + icoSizes.length * 16;
const entries = [];
icoSizes.forEach((s, i) => {
  const e = Buffer.alloc(16);
  e[0] = s === 256 ? 0 : s;
  e[1] = s === 256 ? 0 : s;
  e.writeUInt16LE(1, 4); // planes
  e.writeUInt16LE(32, 6); // bpp
  e.writeUInt32LE(blobs[i].length, 8);
  e.writeUInt32LE(offset, 12);
  offset += blobs[i].length;
  entries.push(e);
});
writeFileSync(join(OUT, "icon.ico"), Buffer.concat([header, ...entries, ...blobs]));

console.log(`OK: ikon dibuat di ${OUT}`);
