from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

#Kết nối SQLite3
def get_db():
    conn = sqlite3.connect('books.db')
    try:
        yield conn
    finally:
        conn.close()

#Tạo bảng
def init_db():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id integer primary key autoincrement,
            title text not null,
            author text not null,
            year integer not null
        )
    ''')
    conn.commit()
    conn.close()
    
init_db()

class Book(BaseModel):
    title: str
    author: str
    year: int

class BookOut(Book):
    id: int

@app.post("/books", response_model=BookOut)
def create_book(book: Book):
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute("Insert into books (title, author, year) values(?, ?, ?)", (book.title, book.author, book.year))
    conn.commit()
    book_id = cursor.lastrowid
    conn.close()
    return {**book.dict(), 'id': book_id}

@app.get("/books",response_model=list[BookOut])
def get_book():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute("Select id, title, author, year from books")
    rows = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'title': row[1], 'author': row[2], 'year': row[3]} for row in rows]
