from fastapi import HTTPException
from functions.db import *

def get_items():
        mydb=defineDB()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM barang")
        myresult = mycursor.fetchall()
        mycursor.close()
        close_db_connection(mydb, "all_barang")
        item_list = []
        for x in myresult:
            items = {
                'result_id' : x[0],
                'result_name' : x[1],
                'result_price' : x[2],
                'result_buy_price' : x[3],
                'result_categories' : x[4],
                'result_kulon' : x[5],
                'result_toko' : x[6],
                'result_pink' : x[7],
                'result_wetan' : x[8],
                'result_kedungsari' : x[9],
                'result_stock' : x[5] + x[6] + x[7] + x[8] + x[9]
            }
            item_list.append(items)
        return item_list