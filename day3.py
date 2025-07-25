from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

#Kết nối SQLite3
def get_db():
    conn = sqlite3('users.db')
    try:
        yield conn
    finally:
        conn.close()
        
#Tạo bảng
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXIST users (
            id INTEGER PRIMARY  KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL 
        )
                   ''')
    conn.commit()
    conn.close()
    