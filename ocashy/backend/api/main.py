from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination, paginate, Params
from fastapi.responses import FileResponse
from functions.data import *
from functions.pdf import *
from pydantic import BaseModel, Field
try:
    import mysql.connector
except ImportError:
    mysql = None

app = FastAPI()

import threading
import time

def start_sync_loop():
    time.sleep(5) # Small initial delay
    while True:
        try:
            from functions.db import sync_mysql_to_sqlite
            sync_mysql_to_sqlite()
        except Exception as e:
            print("[Sync Loop] Background sync error:", e)
        time.sleep(600)

@app.on_event("startup")
async def startup_event():
    sync_thread = threading.Thread(target=start_sync_loop, daemon=True)
    sync_thread.start()

# Define the data model
class Item(BaseModel):
    Product: str = Field(alias='itemName')
    Satuan_Harga: int = Field(alias='satuanHarga')
    Quantity: int = Field(alias='quantity')
    Discount: int = Field(alias='discountPercentage')
    Discounted_Amount: int = Field(alias='discountAmount')
    Warehouse: str = Field(alias='warehouse')
    Price: int = Field(alias='totalPrice')
class ItemUpdate(BaseModel):
    id_barang: str
    nama: str = None
    hargaJual: int = None
    hargaBeli: int = None
    id_kategori: str = None
    kulon: int = None
    toko: int = None
    pink: int = None
    wetan: int = None
    kedungsari: int = None
    
def get_items2(page: int, limit: int):
    mydb = defineDB()
    if mydb is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    mycursor = None
    try:
        mycursor = mydb.cursor()

        # Count total items
        mycursor.execute("SELECT COUNT(*) FROM barang")
        total_count = mycursor.fetchone()[0]

        # Fetch items with pagination
        offset = (page - 1) * limit
        mycursor.execute("SELECT * FROM barang LIMIT %s OFFSET %s", (limit, offset))
        myresult = mycursor.fetchall()
    finally:
        if mycursor is not None:
            mycursor.close()
        close_db_connection(mydb, "all_barang")

    item_list = []
    for x in myresult:
        items = {
            'result_id': x[0],
            'result_name': x[1],
            'result_price': x[2],
            'result_buy_price': x[3],
            'result_categories': x[4],
            'result_kulon': x[5],
            'result_toko': x[6],
            'result_pink': x[7],
            'result_wetan': x[8],
            'result_kedungsari': x[9],
            'result_stock': x[5] + x[6] + x[7] + x[8] + x[9]
        }
        item_list.append(items)
    return item_list, total_count
    
def get_current_values(id_barang):
    mydb = defineDB()
    if mydb is None:
        return None
    cursor = None
    try:
        cursor = mydb.cursor(dictionary=True)  # Use dictionary=True to get results as dictionaries
        cursor.execute("SELECT * FROM barang WHERE Id_barang = %s", (id_barang,))
        result = cursor.fetchone()
        return result
    finally:
        if cursor is not None:
            cursor.close()
        close_db_connection(mydb, "your_database_name")  # Adjust as needed

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    mydb = defineDB()
    db_type = "mysql"
    if mydb is not None:
        if isinstance(mydb, SQLiteConnectionWrapper):
            db_type = "sqlite"
        close_db_connection(mydb, "root_check")
    else:
        db_type = "none"
    return {"Hello": "World", "database": db_type}

@app.get("/barang")
def GETitems():
    try:
        return {
            "Status" : "OK",
            "Items" : get_items()
        }
    except:
        raise HTTPException(status_code=533, detail="Error on server side")

def search_by_name(name: str, page: int, limit: int):
    mydb = defineDB()
    if mydb is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    mycursor = None
    try:
        mycursor = mydb.cursor()

        # Escaping the % for SQL LIKE and adding it for search pattern
        search_pattern = f"%{name}%"

        # Count total items that match the search pattern
        mycursor.execute("SELECT COUNT(*) FROM barang WHERE LOWER(Nama) LIKE LOWER(%s)", (search_pattern,))
        total_count = mycursor.fetchone()[0]

        # Fetch items with pagination and search filter
        offset = (page - 1) * limit
        mycursor.execute("SELECT * FROM barang WHERE LOWER(Nama) LIKE LOWER(%s) LIMIT %s OFFSET %s", 
                         (search_pattern, limit, offset))
        myresult = mycursor.fetchall()
    finally:
        if mycursor is not None:
            mycursor.close()
        close_db_connection(mydb, "search_barang")
    item_list = []
    for x in myresult:
        items = {
            'result_id': x[0],
            'result_name': x[1],
            'result_price': x[2],
            'result_buy_price': x[3],
            'result_categories': x[4],
            'result_kulon': x[5],
            'result_toko': x[6],
            'result_pink': x[7],
            'result_wetan': x[8],
            'result_kedungsari': x[9],
            'result_stock': x[5] + x[6] + x[7] + x[8] + x[9]
        }
        item_list.append(items)
    return item_list, total_count
    
@app.get("/search")
def search_items(name: str = '', page: int = Query(default=1, ge=1), limit: int = Query(default=10, ge=1)):
    try:
        items, total_count = search_by_name(name, page, limit)
        total_pages = (total_count + limit - 1) // limit
        return {
            "Status": "OK",
            "TotalPages": total_pages,
            "CurrentPage": page,
            "ItemsPerPage": limit,
            "Items": items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/barang/limit")
def GETitems(page: int = Query(default=1, ge=1), limit: int = Query(default=10, ge=1)):
    try:
        items, total_count = get_items2(page, limit)
        total_pages = (total_count + limit - 1) // limit  # calculate the number of total pages
        return {
            "Status": "OK",
            "TotalPages": total_pages,
            "CurrentPage": page,
            "ItemsPerPage": limit,
            "Items": items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/pdfs")
async def list_pdfs():
    folder_path = os.path.join(os.getcwd(), "..", "..", "receipts")  # set folder to ../../receipts
    os.makedirs(folder_path, exist_ok=True)
    try:
        files = os.listdir(folder_path)
        pdf_files = [file for file in files if file.endswith('.pdf')]
        return {"pdf_files": pdf_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pdfs/{pdf_name}")
async def get_pdf(pdf_name: str):
    folder_path = os.path.join(os.getcwd(), "..", "..", "receipts")  # set folder to ../../receipts
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, pdf_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf')
    else:
        raise HTTPException(status_code=404, detail="File not found")
    
@app.post("/items/{bayar}/{tipe}")
async def make_pdf(bayar: int, items: List[Item], tipe : str):
    # Ensure receipts folder exists
    folder_path = os.path.join(os.getcwd(), "..", "..", "receipts")
    os.makedirs(folder_path, exist_ok=True)
    # Convert each Item object to a dictionary before passing to create_pdf
    items_dict = [item.dict() for item in items]
    return create_pdf(bayar, items_dict, tipe)

@app.post("/print-pdf")
async def print_pdf(filename: str):
    folder_path = os.path.join(os.getcwd(), "..", "..", "receipts")
    file_path = os.path.normpath(os.path.join(folder_path, filename))
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"PDF file not found at: {file_path}")
        
    try:
        import subprocess
        local_app_data = os.environ.get("LocalAppData", "")
        sumatra_path = os.path.join(local_app_data, "SumatraPDF", "SumatraPDF.exe")
        if not os.path.exists(sumatra_path):
            prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            sumatra_path = os.path.join(prog_files, "SumatraPDF", "SumatraPDF.exe")
            if not os.path.exists(sumatra_path):
                sumatra_path = "SumatraPDF.exe"
                
        cmd = [
            sumatra_path,
            "-print-to-default",
            "-print-settings", "paper=A4,noscale,landscape",
            file_path
        ]
        
        print("Executing print command:", " ".join(cmd))
        subprocess.run(cmd, check=True)
        return {"status": "success", "message": f"Sent {filename} to printer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute SumatraPDF: {str(e)}")


@app.get("/backup-db")
def backup_db():
    mydb = defineDB()
    if mydb is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    cursor = None
    try:
        cursor = mydb.cursor()
        cursor.execute("SELECT id_barang, nama, hargaJual, hargaBeli, id_kategori, kulon, toko, pink, wetan, kedungsari FROM barang")
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read database: {str(e)}")
    finally:
        if cursor is not None:
            cursor.close()
        close_db_connection(mydb, "backup")

    # Generate SQL dump
    sql_lines = []
    sql_lines.append("-- Ocashy Database SQL Backup")
    sql_lines.append("-- Generated by Ocashy Desktop App")
    sql_lines.append("")
    sql_lines.append("DROP TABLE IF EXISTS barang;")
    sql_lines.append("""CREATE TABLE barang (
    id_barang VARCHAR(255) PRIMARY KEY,
    nama VARCHAR(255) NOT NULL,
    hargaJual INT NOT NULL DEFAULT 0,
    hargaBeli INT NOT NULL DEFAULT 0,
    id_kategori VARCHAR(255) NOT NULL DEFAULT '',
    kulon INT NOT NULL DEFAULT 0,
    toko INT NOT NULL DEFAULT 0,
    pink INT NOT NULL DEFAULT 0,
    wetan INT NOT NULL DEFAULT 0,
    kedungsari INT NOT NULL DEFAULT 0
);""")
    sql_lines.append("")
    
    for row in rows:
        # Escape single quotes in product name
        escaped_name = row[1].replace("'", "''")
        val_str = f"('{row[0]}', '{escaped_name}', {row[2]}, {row[3]}, '{row[4]}', {row[5]}, {row[6]}, {row[7]}, {row[8]}, {row[9]})"
        sql_lines.append(f"INSERT INTO barang (id_barang, nama, hargaJual, hargaBeli, id_kategori, kulon, toko, pink, wetan, kedungsari) VALUES {val_str};")
        
    sql_content = "\n".join(sql_lines)
    
    backups_dir = os.path.join(os.getcwd(), "..", "..", "backups")
    os.makedirs(backups_dir, exist_ok=True)
    
    import datetime
    now = datetime.datetime.now()
    filename = f"ocashy_backup_{now.strftime('%d-%m-%Y_%H-%M-%S')}.sql"
    file_path = os.path.join(backups_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(sql_content)
        
    return FileResponse(
        file_path,
        media_type="application/sql",
        filename=filename
    )


class MigrationRequest(BaseModel):
    host: str
    dbase: str
    duser: str
    dpw: str

def update_env_file(host, db_name, user, password):
    env_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
    new_values = {
        "dip": f'"{host}"',
        "dbase": f'"{db_name}"',
        "duser": f'"{user}"',
        "dpw": f'"{password}"'
    }
    
    updated_keys = set()
    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue
            
        parts = stripped.split("=", 1)
        if len(parts) == 2:
            key = parts[0].strip()
            if key in new_values:
                new_lines.append(f'{key} = {new_values[key]}\n')
                updated_keys.add(key)
                continue
        new_lines.append(line)
        
    for key, val in new_values.items():
        if key not in updated_keys:
            new_lines.append(f'{key} = {val}\n')
            
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

@app.post("/migrate-db")
async def migrate_db(req: MigrationRequest):
    if mysql is None:
        raise HTTPException(status_code=500, detail="mysql-connector package tidak terpasang di server.")

    db_host = req.host
    db_port = 3306
    if ":" in req.host:
        parts = req.host.split(":", 1)
        db_host = parts[0]
        try:
            db_port = int(parts[1])
        except ValueError:
            pass

    # First, try to auto-create the database if it doesn't exist
    try:
        admin_conn = mysql.connector.connect(
            user=req.duser,
            password=req.dpw,
            host=db_host,
            port=db_port,
            connection_timeout=15
        )
        admin_cursor = admin_conn.cursor()
        admin_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {req.dbase}")
        admin_conn.commit()
        admin_cursor.close()
        admin_conn.close()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Gagal menghubungkan ke server MySQL atau gagal membuat database '{req.dbase}'.\nError: {str(e)}"
        )

    try:
        new_db = mysql.connector.connect(
            database=req.dbase,
            user=req.duser,
            password=req.dpw,
            host=db_host,
            port=db_port,
            connection_timeout=15
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Gagal menghubungkan ke database '{req.dbase}'.\nError: {str(e)}"
        )
        
    try:
        current_db = defineDB()
        if current_db is None:
            raise HTTPException(status_code=500, detail="Database saat ini gagal dihubungi")
            
        current_cursor = current_db.cursor()
        current_cursor.execute("SELECT id_barang, nama, hargaJual, hargaBeli, id_kategori, kulon, toko, pink, wetan, kedungsari FROM barang")
        rows = current_cursor.fetchall()
        current_cursor.close()
        close_db_connection(current_db, "current_migrate")
    except Exception as e:
        new_db.close()
        raise HTTPException(status_code=500, detail=f"Gagal membaca data dari database saat ini: {str(e)}")

    try:
        new_cursor = new_db.cursor()
        new_cursor.execute("""
            CREATE TABLE IF NOT EXISTS barang (
                id_barang VARCHAR(255) PRIMARY KEY,
                nama VARCHAR(255) NOT NULL,
                hargaJual INT NOT NULL DEFAULT 0,
                hargaBeli INT NOT NULL DEFAULT 0,
                id_kategori VARCHAR(255) NOT NULL DEFAULT '',
                kulon INT NOT NULL DEFAULT 0,
                toko INT NOT NULL DEFAULT 0,
                pink INT NOT NULL DEFAULT 0,
                wetan INT NOT NULL DEFAULT 0,
                kedungsari INT NOT NULL DEFAULT 0
            )
        """)
        new_cursor.execute("DELETE FROM barang")
        new_db.commit()
        
        sql = "INSERT INTO barang (id_barang, nama, hargaJual, hargaBeli, id_kategori, kulon, toko, pink, wetan, kedungsari) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        # Batch insert in chunks of 100 rows to prevent remote timeouts
        chunk_size = 100
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            new_cursor.executemany(sql, chunk)
            new_db.commit()
            
        new_cursor.close()
        new_db.close()
    except Exception as e:
        new_db.close()
        raise HTTPException(status_code=500, detail=f"Gagal menulis data ke database baru: {str(e)}")

    try:
        update_env_file(req.host, req.dbase, req.duser, req.dpw)
        
        os.environ["dip"] = req.host
        os.environ["dbase"] = req.dbase
        os.environ["duser"] = req.duser
        os.environ["dpw"] = req.dpw
        
        import functions.db
        functions.db.dip = req.host
        functions.db.dbase = req.dbase
        functions.db.duser = req.duser
        functions.db.dpw = req.dpw
        functions.db.db_initialized = False
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data berhasil disalin, tetapi gagal memperbarui file .env: {str(e)}")

    return {"status": "success", "message": f"Berhasil migrasi data ke database {req.dbase} dan memperbarui file .env"}


@app.post("/items/")
async def create_item(item: ItemUpdate):
    mydb = defineDB()
    if mydb is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    mycursor = None
    try:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM barang WHERE id_barang = %s", (item.id_barang,))
        result = mycursor.fetchone()
        if result is not None:
            raise HTTPException(status_code=400, detail="Item with this id already exists")
        sql = "INSERT INTO barang (id_barang, nama, hargaJual, hargaBeli, id_kategori, kulon, toko, pink, wetan, kedungsari) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (item.id_barang, item.nama, item.hargaJual, item.hargaBeli, item.id_kategori, item.kulon, item.toko, item.pink, item.wetan, item.kedungsari)
        mycursor.execute(sql, val)
        mydb.commit()
    finally:
        if mycursor is not None:
            mycursor.close()
        close_db_connection(mydb, "create_item")
    return {"message": f"Item {item.id_barang} was successfully created."}

@app.delete("/items/{id_barang}")
async def delete_item(id_barang: str):
    mydb = defineDB()
    if mydb is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    mycursor = None
    try:
        mycursor = mydb.cursor()

        # Check if the item exists
        mycursor.execute("SELECT * FROM barang WHERE id_barang = %s", (id_barang,))
        result = mycursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Item not found")

        # Delete the item
        sql = "DELETE FROM barang WHERE id_barang = %s"
        mycursor.execute(sql, (id_barang,))
        mydb.commit()
    finally:
        if mycursor is not None:
            mycursor.close()
        close_db_connection(mydb, "delete_item")

    return {"message": f"Item {id_barang} was successfully deleted."}

@app.put("/update-item/{id_barang}")
async def update_item(id_barang: str, item: ItemUpdate):
    current_values = get_current_values(id_barang)
    if not current_values:
        raise HTTPException(status_code=404, detail="Item not found")

    # Normalize keys to lowercase to avoid case sensitivity mismatches
    current_values = {k.lower(): v for k, v in current_values.items()}

    mydb = defineDB()
    if mydb is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = None
    try:
        cursor = mydb.cursor()
        # Use the existing values if no new value is provided
        update_values = {
            "nama": item.nama if item.nama is not None else current_values.get('nama'),
            "hargaJual": item.hargaJual if item.hargaJual is not None else current_values.get('hargajual'),
            "hargaBeli": item.hargaBeli if item.hargaBeli is not None else current_values.get('hargabeli'),
            "id_kategori": item.id_kategori if item.id_kategori is not None else current_values.get('id_kategori'),
            "kulon": item.kulon if item.kulon is not None else current_values.get('kulon'),
            "toko": item.toko if item.toko is not None else current_values.get('toko'),
            "pink": item.pink if item.pink is not None else current_values.get('pink'),
            "wetan": item.wetan if item.wetan is not None else current_values.get('wetan'),
            "kedungsari": item.kedungsari if item.kedungsari is not None else current_values.get('kedungsari'),
        }
        sql = """
            UPDATE barang 
            SET Nama = %s, HargaJual = %s, HargaBeli = %s, Id_kategori = %s, 
                Kulon = %s, Toko = %s, Pink = %s, Wetan = %s, Kedungsari = %s 
            WHERE Id_barang = %s
        """
        cursor.execute(sql, (
            update_values['nama'], update_values['hargaJual'], update_values['hargaBeli'], update_values['id_kategori'],
            update_values['kulon'], update_values['toko'], update_values['pink'], update_values['wetan'], update_values['kedungsari'],
            id_barang
        ))
        mydb.commit()
    except Exception as error:
        if mydb is not None:
            mydb.rollback()  # Rollback in case of any error
        raise HTTPException(status_code=500, detail=f"Database update failed: {error}")
    finally:
        if cursor is not None:
            cursor.close()
        close_db_connection(mydb, "update_item")

    # Fetch and return the updated values
    updated_values = get_current_values(id_barang)
    if updated_values:
        return updated_values
    else:
        raise HTTPException(status_code=404, detail="Failed to fetch updated item")