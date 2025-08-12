#Product API
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg2.extensions import connection
import psycopg2

app = FastAPI()

class Category(BaseModel):
    name: str
    
class CategoryOut(Category):
    id: int

class Product(BaseModel):
    name: str
    price: float
    
class ProductOut(Product):
    id: int
    category: str
DB_CONFIG = {
    'host': 'localhost',
    'database': 'DB_API',
    'user': 'postgres',
    'password': '1234'
}

def get_db() -> connection:
    return psycopg2.connect(**DB_CONFIG)

@app.get("/products",response_model=list[ProductOut])
def get_products():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            SELECT p.id, p.name, price, c.name
            FROM products p
            JOIN categories c
            ON category_id = c.id
                    ''')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": row[0], "name": row[1], "price": float(row[2]) , "category": row[3]} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Database error: {str(e)}")