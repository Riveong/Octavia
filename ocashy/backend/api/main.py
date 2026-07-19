from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination, paginate, Params
from fastapi.responses import FileResponse
from functions.data import *
from functions.pdf import *
from pydantic import BaseModel, Field
import os
import mysql.connector

app = FastAPI()

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

origins = [
    "http://localhost:5000",
    "http://localhost:8080"# Allow requests from our frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

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
    except mysql.connector.Error as error:
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