use std::process::Command;
use tauri_plugin_sql::{Migration, MigrationKind};

#[tauri::command]
async fn print_pdf_via_sumatra(
    pdf_path: String,
    printer_name: Option<String>,
    sumatra_path: Option<String>,
) -> Result<String, String> {
    let executable = sumatra_path
        .filter(|p| !p.trim().is_empty())
        .unwrap_or_else(|| "SumatraPDF.exe".to_string());

    let mut cmd = Command::new(&executable);

    if let Some(printer) = printer_name.filter(|p| !p.trim().is_empty()) {
        cmd.arg("-print-to").arg(printer);
    } else {
        cmd.arg("-print-to-default");
    }

    cmd.arg("-print-settings").arg("noscale");
    cmd.arg(&pdf_path);

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    match cmd.status() {
        Ok(status) => {
            if status.success() {
                Ok("Struk berhasil dikirim ke printer!".to_string())
            } else {
                Err(format!(
                    "SumatraPDF keluar dengan error code: {:?}",
                    status.code()
                ))
            }
        }
        Err(e) => Err(format!(
            "Gagal menjalankan SumatraPDF. Pastikan program terinstal dan lokasi benar.\nError: {}",
            e
        )),
    }
}

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
        .invoke_handler(tauri::generate_handler![print_pdf_via_sumatra])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
