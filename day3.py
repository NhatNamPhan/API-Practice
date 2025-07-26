from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

#Kết nối SQLite3
def get_db():
    conn = sqlite3.connect('users.db')
    try:
        yield conn
    finally:
        conn.close()
        
#Tạo bảng
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL 
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class User(BaseModel):
    name: str
    email: str

class UserOut(User):
    id: int

@app.post('/users', response_model=UserOut)
def create_user(user: User):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (user.name, user.email))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return {**user.dict(), "id": user_id}

@app.get('/users', response_model=list[UserOut])
def get_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "email": row[2]} for row in rows]

@app.get('/users/{user_id}', response_model=UserOut)
def get_user(user_id: int):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "email": row[2]}
    raise HTTPException(status_code=404, detail="User not found")

@app.put('/users/{user_id}', response_model=UserOut)
def update_user(user_id: int, user: User):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (user.name, user.email, user_id))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conn.close()
    return {**user.dict(), "id": user_id}

@app.delete('/users/{user_id}')
def delete_user(user_id: int):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conn.close()
    return {"message": f"User with id {user_id} has been deleted"}