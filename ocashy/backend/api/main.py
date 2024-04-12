from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination, paginate, Params
from fastapi.responses import FileResponse
from functions.data import *
from functions.pdf import *
from pydantic import BaseModel, Field
import os

app = FastAPI()

# Define the data model
class Item(BaseModel):
    Product: str = Field(alias='itemName')
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
    
def get_current_values(id_barang):
    mydb = defineDB()
    cursor = mydb.cursor(dictionary=True)  # Use dictionary=True to get results as dictionaries
    try:
        cursor.execute("SELECT * FROM barang WHERE Id_barang = %s", (id_barang,))
        result = cursor.fetchone()
        return result
    finally:
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
    
@app.get("/pdfs")
async def list_pdfs():
    folder_path = os.path.join(os.getcwd(), "..", "..", "receipts")  # set folder to ../../receipts
    files = os.listdir(folder_path)
    pdf_files = [file for file in files if file.endswith('.pdf')]
    return {"pdf_files": pdf_files}

@app.get("/pdfs/{pdf_name}")
async def get_pdf(pdf_name: str):
    folder_path = os.path.join(os.getcwd(), "..", "..", "receipts")  # set folder to ../../receipts
    file_path = os.path.join(folder_path, pdf_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf')
    else:
        raise HTTPException(status_code=404, detail="File not found")
    
@app.post("/items/{bayar}/{tipe}")
async def make_pdf(bayar: int, items: List[Item], tipe : str):
    # Convert each Item object to a dictionary before passing to create_pdf
    items_dict = [item.dict() for item in items]
    return create_pdf(bayar, items_dict, tipe)

@app.post("/items/")
async def create_item(item: ItemUpdate):
    mydb = defineDB()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM barang WHERE id_barang = %s", (item.id_barang,))
    result = mycursor.fetchone()
    if result is not None:
        raise HTTPException(status_code=400, detail="Item with this id already exists")
    sql = "INSERT INTO barang (id_barang, nama, hargaJual, hargaBeli, id_kategori, kulon, toko, pink, wetan, kedungsari) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (item.id_barang, item.nama, item.hargaJual, item.hargaBeli, item.id_kategori, item.kulon, item.toko, item.pink, item.wetan, item.kedungsari)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()
    mydb.close()
    return {"message": f"Item {item.id_barang} was successfully created."}

@app.delete("/items/{id_barang}")
async def delete_item(id_barang: str):
    mydb = defineDB()
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

    mycursor.close()
    mydb.close()

    return {"message": f"Item {id_barang} was successfully deleted."}

@app.put("/update-item/{id_barang}")
async def update_item(id_barang: str, item: ItemUpdate):
    current_values = get_current_values(id_barang)
    if not current_values:
        raise HTTPException(status_code=404, detail="Item not found")

    mydb = defineDB()
    cursor = mydb.cursor()
    try:
        # Use the existing values if no new value is provided
        update_values = {
            "nama": item.nama if item.nama is not None else current_values['nama'],
            "hargaJual": item.hargaJual if item.hargaJual is not None else current_values['hargaJual'],
            "hargaBeli": item.hargaBeli if item.hargaBeli is not None else current_values['hargaBeli'],
            "id_kategori": item.id_kategori if item.id_kategori is not None else current_values['id_kategori'],
            "kulon": item.kulon if item.kulon is not None else current_values['kulon'],
            "toko": item.toko if item.toko is not None else current_values['toko'],
            "pink": item.pink if item.pink is not None else current_values['pink'],
            "wetan": item.wetan if item.wetan is not None else current_values['wetan'],
            "kedungsari": item.kedungsari if item.kedungsari is not None else current_values['kedungsari'],
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
        mydb.rollback()  # Rollback in case of any error
        raise HTTPException(status_code=500, detail=f"Database update failed: {error}")
    finally:
        cursor.close()
        close_db_connection(mydb, "your_database_name")  # Make sure to replace "your_database_name" with your actual database name

    # Fetch and return the updated values
    updated_values = get_current_values(id_barang)
    if updated_values:
        return updated_values
    else:
        raise HTTPException(status_code=404, detail="Failed to fetch updated item")