from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg2.extensions import connection
import psycopg2

app = FastAPI()

class Contact(BaseModel):
    name: str
    phone: str

class ContactOut(Contact):
    id: int

DB_CONFIG = {
    'host': 'localhost',
    'database': 'DB_API',
    'user': 'postgres',
    'password': '1234'
}

def get_db() -> connection:
    return psycopg2.connect(**DB_CONFIG)

@app.get("/contacts",response_model=list[ContactOut])
def get_contacts():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts")
        rows = cur.fetchall()
        conn.close()
        return [{"id": row[0], "name": row[1], "phone": row[2]} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/contacts",response_model=ContactOut)
def insert_contact(contact: Contact):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s) RETURNING id",(contact.name,contact.phone))
        contact_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        return {**contact.model_dump(),"id":contact_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")