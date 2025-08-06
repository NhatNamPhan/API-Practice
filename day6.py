from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

#Kết nối SQLite3
def get_db():
    conn = sqlite3.connect("student.db")
    try:
        yield conn
    finally:
        conn.close()

#Tạo bảng
def init_db():
    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_code TEXT NOT NULL,
            gpa FLOAT NOT NULL
        )           
                   ''')
    conn.commit()
    conn.close()

init_db()

class Student(BaseModel):
    name: str
    student_code: str
    gpa: float

class StudentOut(Student):
    id: int

@app.post("/student",response_model=Student)
def insert_student(student: Student):
    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO student (name, student_code, gpa) VALUES (?, ?, ?)",(student.name, student.student_code, student.gpa))
    conn.commit()
    stu_id = cursor.lastrowid
    conn.close()
    return {**student.dict(),"id": stu_id}

@app.get("/student",response_model=list[StudentOut])
def get_student():
    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "student_code": row[2], "gpa": row[3]} for row in rows]

@app.get("/student/highgpa",response_model=list[StudentOut])
def get_student_highgpa():
    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE gpa > 3.2")
    rows = cursor.fetchall()
    conn.close()
    if rows:
        return [{"id": row[0], "name": row[1], "student_code": row[2], "gpa": row[3]} for row in rows]
    raise HTTPException(status_code=404,detail="No student gpa > 3.2 ")

@app.delete("/student/{std_id}")
def delete_std(std_id: int):
    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE id = ?",(std_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail='Student not found')
    conn.close()
    return {"message": f"Student with id {std_id} has been deleted"}
