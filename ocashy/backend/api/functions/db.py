import mysql.connector
from decouple import config
from dotenv import load_dotenv
import os

load_dotenv()
dbase = os.getenv("dbase")
duser = os.getenv("duser")
dpw = os.getenv("dpw")
dip = os.getenv("dip")

# Define a function to open database connection
def open_db_connection(db_name, user, password, host):
    try:
        mydb = mysql.connector.connect(database=db_name, user=user, password=password, host=host)
        print("Opened connection to database:", db_name)
        return mydb
    except mysql.connector.Error as e:
        print("Failed to open connection to database:", e)
        return None

# Define a function to close database connection
def close_db_connection(mydb, db_name):
    if mydb:
        try:
            mydb.close()
            print("Closed connection to database:", db_name)
        except mysql.connector.Error as e:
            print("Failed to close connection to database:", e)



def defineDB():
   mydb=open_db_connection(
       dbase,
       duser,
       dpw,
       dip,
   )
   return mydb