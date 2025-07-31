from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

#Kết nối SQLite3
def get_db():
    conn = sqlite3.connect("phonebook.db")
    try:
        yield conn
    finally:
        conn.close()

#Tạo bảng
def init_db():
    conn = sqlite3.connect("phonebook.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phonebook (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL
        )
                   ''')
    conn.commit()
    conn.close()

init_db()

class PhoneBook(BaseModel):
    name: str
    phone: str
    address: str
    
class PhoneBookOut(PhoneBook):
    id: int

@app.post("/phonebook",response_model=PhoneBook)
def create_phonebook(phonebook: PhoneBook):
    conn = sqlite3.connect("phonebook.db")
    cursor = conn.cursor()
    cursor.execute("Insert into phonebook (name, phone, address) values (?, ?, ?)",(phonebook.name, phonebook.phone, phonebook.address))
    conn.commit()
    pb_id = cursor.lastrowid
    conn.close()
    return {**phonebook.dict(), "id": pb_id}

@app.get("/phonebook",response_model=list[PhoneBookOut])
def get_phonebook():
    conn = sqlite3.connect("phonebook.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM phonebook")
    rows = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'name': row[1], 'phone': row[2], 'address': row[3]} for row in rows]

@app.delete("/phonebook/{pb_id}")
def delete_id(pb_id: int):
    conn = sqlite3.connect("phonebook.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phonebook WHERE id = ?", (pb_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="PhoneBook not found")
    conn.close()
    return {"message": f"PhoneBook with id {pb_id} has been deleted"}

@app.get("/phonebook/search",response_model=PhoneBookOut)
def search_name(name: str):
    conn = sqlite3.connect("phonebook.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM phonebook WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "phone": row[2], "address": row[3]}
    raise HTTPException(status_code=404,detail="PhoneBook not found")