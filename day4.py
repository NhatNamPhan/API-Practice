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
def get_books():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute("Select * from books")
    rows = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'title': row[1], 'author': row[2], 'year': row[3]} for row in rows]

@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "title": row[1], "author": row[2], "year": row[3]}
    raise HTTPException(status_code=404, detail="Book not found")

@app.put("/books/{book_id}", response_model=BookOut)
def update_book(book_id: int, book: Book):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE books set title = ?, author = ?, year = ? WHERE id = ?",(book.title, book.author,book.year, book_id))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404,detail="Book not found")
    conn.close()
    return {**book.dict(), "id":book_id}

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?",(book_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404,detail="Book not found")
    conn.close()
    return {"message": f"Book with id {book_id} has been deleted"}