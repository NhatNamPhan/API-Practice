from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

#Kết nối SQLite3
def get_db():
    conn = sqlite3.connect('tasks.db')
    try:
        yield conn
    finally:
        conn.close()
        
#Tạo bảng
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0 NOT NULL
        )
                   ''')
    conn.commit()
    conn.close()
    
init_db()

class Task(BaseModel):
    title: str
    completed: bool = False
    
class TaskStatusUpdate(BaseModel):
    completed: bool
    
class TaskOut(Task):
    id: int

@app.post("/task",response_model=Task)
def insert_task(task: Task):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, completed) VALUES (?, ?)",(task.title,int(task.completed)))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {**task.dict(), "id": task_id}

@app.put("/task/{task_id}",response_model=Task)
def update_task(task_id: int, status: TaskStatusUpdate):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks set completed = ? WHERE id = ?",(int(status.completed),task_id))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404,detail="Task not found")
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return {"id": row[0], "title": row[1], "completed": bool(row[2])}

@app.delete("/task/{task_id}")
def delete_task(task_id: int):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?",(task_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404,detail="Task not found")
    conn.close()
    return {"message": f"Task with id {task_id} has been deleted"}

@app.get("/task/incomplete",response_model=list[TaskOut])
def get_incomp_task():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE completed == 0")
    rows = cursor.fetchall()
    conn.close()
    if rows:
        return [{"id": row[0], "title": row[1], "completed": bool(row[2])} for row in rows]
    raise HTTPException(status_code=404,detail="All tasks have been completed")

@app.get("/task",response_model=list[TaskOut])
def get_tasks():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "title": row[1], "completed": bool(row[2])} for row in rows]
    