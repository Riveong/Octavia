use tauri_plugin_sql::{Migration, MigrationKind};

pub fn run() {
    // Skema dikelola Drizzle (drizzle/*.sql); dijalankan otomatis di sini
    // saat frontend membuka "sqlite:ocashy.db". Tambah migrasi baru dengan
    // `npm run db:generate` lalu daftarkan filenya di list ini.
    let migrations = vec![Migration {
        version: 1,
        description: "init",
        sql: include_str!("../../drizzle/0000_init.sql"),
        kind: MigrationKind::Up,
    }];

    tauri::Builder::default()
        .plugin(
            tauri_plugin_sql::Builder::default()
                .add_migrations("sqlite:ocashy.db", migrations)
                .build(),
        )
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_opener::init())
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
