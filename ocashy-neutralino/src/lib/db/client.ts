import initSqlJs from "sql.js";
import { drizzle } from "drizzle-orm/sqlite-proxy";
import * as schema from "./schema";
// @ts-ignore
import initMigrationSql from "../../../drizzle/0000_init.sql?raw";

declare const Neutralino: any;

let dbInstance: any = null;
let dbPath: string = "";

async function ensureDir(path: string) {
  try {
    await Neutralino.filesystem.createDirectory(path);
  } catch (err: any) {
    if (err.code !== "NE_FS_DIRALR") {
      throw err;
    }
  }
}

export async function getSqlite(): Promise<any> {
  if (!dbInstance) {
    const appData = await Neutralino.os.getPath("data");
    const appFolder = `${appData}/ocashy`;
    await ensureDir(appFolder);

    dbPath = `${appFolder}/ocashy.db`;

    let dbData: Uint8Array | null = null;
    try {
      const bytes = await Neutralino.filesystem.readBinaryFile(dbPath);
      dbData = new Uint8Array(bytes);
    } catch (err: any) {
      console.log("Database file not found, initializing fresh database...", err);
    }

    const SQL = await initSqlJs({
      locateFile: (file) => `./${file}`,
    });

    if (dbData) {
      dbInstance = new SQL.Database(dbData);
    } else {
      dbInstance = new SQL.Database();
      // Run the initial migration
      dbInstance.run(initMigrationSql);
      
      // Save initial DB
      const data = dbInstance.export();
      await Neutralino.filesystem.writeBinaryFile(dbPath, data.buffer);
    }
  }
  return dbInstance;
}

function isSelect(sql: string): boolean {
  const s = sql.trimStart().toLowerCase();
  return s.startsWith("select") || s.startsWith("pragma") || s.startsWith("with");
}

export const db = drizzle<typeof schema>(
  async (sql, params, method) => {
    const dbi = await getSqlite();

    const sqlParams = params as any[];

    if (!isSelect(sql)) {
      dbi.run(sql, sqlParams);
      
      // Save changes to disk on mutation
      const data = dbi.export();
      await Neutralino.filesystem.writeBinaryFile(dbPath, data.buffer);
      
      return { rows: [] };
    }

    const res = dbi.exec(sql, sqlParams);
    const values = res.length > 0 ? res[0].values : [];
    
    return { rows: method === "get" ? (values[0] ?? []) : values };
  },
  { schema },
);

export { schema };
