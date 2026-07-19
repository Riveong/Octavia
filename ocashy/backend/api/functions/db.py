try:
    import mysql.connector
except ImportError:
    mysql = None
import sqlite3
from decouple import config
from dotenv import load_dotenv
import os

load_dotenv()
dbase = os.getenv("dbase")
duser = os.getenv("duser")
dpw = os.getenv("dpw")
dip = os.getenv("dip")

class SQLiteCursorWrapper:
    def __init__(self, sqlite_cursor, dictionary=False):
        self.cursor = sqlite_cursor
        self.dictionary = dictionary

    def execute(self, sql, params=None):
        # Translate mysql parameter placeholders (%s) to sqlite (?)
        sql_translated = sql.replace('%s', '?')
        if params is None:
            self.cursor.execute(sql_translated)
        else:
            if isinstance(params, list):
                params = tuple(params)
            self.cursor.execute(sql_translated, params)
        return self

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        if self.dictionary:
            return dict(row)
        return tuple(row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        if self.dictionary:
            return [dict(row) for row in rows]
        return [tuple(row) for row in rows]

    def close(self):
        self.cursor.close()

class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    def cursor(self, dictionary=False):
        sqlite_cursor = self.conn.cursor()
        return SQLiteCursorWrapper(sqlite_cursor, dictionary=dictionary)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

def init_sqlite_db(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS barang (
                id_barang TEXT PRIMARY KEY NOT NULL,
                nama TEXT NOT NULL,
                hargaJual INTEGER NOT NULL DEFAULT 0,
                hargaBeli INTEGER NOT NULL DEFAULT 0,
                id_kategori TEXT NOT NULL DEFAULT '',
                kulon INTEGER NOT NULL DEFAULT 0,
                toko INTEGER NOT NULL DEFAULT 0,
                pink INTEGER NOT NULL DEFAULT 0,
                wetan INTEGER NOT NULL DEFAULT 0,
                kedungsari INTEGER NOT NULL DEFAULT 0
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM barang")
        if cursor.fetchone()[0] == 0:
            sample_data = [
                ('B001', 'Contoh Barang A', 15000, 10000, 'K01', 10, 5, 2, 8, 15),
                ('B002', 'Contoh Barang B', 25000, 18000, 'K01', 5, 10, 12, 4, 3),
                ('B003', 'Contoh Barang C', 5000, 3000, 'K02', 100, 50, 40, 60, 80),
            ]
            cursor.executemany("""
                INSERT INTO barang (id_barang, nama, hargaJual, hargaBeli, id_kategori, kulon, toko, pink, wetan, kedungsari)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_data)
            conn.commit()
        cursor.close()
    except Exception as e:
        print("Failed to initialize SQLite schema:", e)

def open_sqlite_connection():
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ocashy_fallback.db")
        print("Connecting to fallback SQLite database at:", db_path)
        conn = sqlite3.connect(db_path)
        init_sqlite_db(conn)
        return SQLiteConnectionWrapper(conn)
    except Exception as e:
        print("Failed to open SQLite database:", e)
        return None

def open_db_connection(db_name, user, password, host):
    if mysql is None:
        print("mysql-connector package not installed, falling back to SQLite...")
        return open_sqlite_connection()

    if not db_name or not user or not host:
        print("MySQL credentials missing, falling back to SQLite...")
        return open_sqlite_connection()

    try:
        mydb = mysql.connector.connect(
            database=db_name, 
            user=user, 
            password=password, 
            host=host,
            connection_timeout=3
        )
        print("Opened connection to database:", db_name)
        return mydb
    except Exception as e:
        print(f"Failed to open MySQL connection ({e}). Falling back to SQLite...")
        return open_sqlite_connection()

# Define a function to close database connection
def close_db_connection(mydb, db_name):
    if mydb:
        try:
            mydb.close()
            print("Closed connection to database:", db_name)
        except Exception as e:
            print("Failed to close connection to database:", e)

def defineDB():
   mydb=open_db_connection(
       dbase,
       duser,
       dpw,
       dip,
   )
   return mydb