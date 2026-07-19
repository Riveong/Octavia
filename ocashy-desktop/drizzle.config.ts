import { defineConfig } from "drizzle-kit";

// Used only to generate SQL migrations into ./drizzle.
// Generated files are applied by the Rust side (tauri-plugin-sql) at startup.
export default defineConfig({
  dialect: "sqlite",
  schema: "./src/lib/db/schema.ts",
  out: "./drizzle",
});
