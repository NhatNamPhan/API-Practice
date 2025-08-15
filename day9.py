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
    
class ProductIn(BaseModel):
    name: str
    price: float
    category_id: int
    
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

@app.post("/products",response_model=ProductOut)
def insert_product(prod: ProductIn):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, price, category_id) VALUES (%s, %s, %s) RETURNING id",(prod.name,prod.price,prod.category_id))
        product_id = cur.fetchone()[0]
        conn.commit()
        cur.execute("SELECT name FROM categories WHERE id = %s", (prod.category_id,))
        category_name = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {
            "id": product_id,
            "name": prod.name,
            "price": prod.price,
            "category": category_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@app.get("/products/{prod_id}",response_model=ProductOut)
def get_prod(prod_id: int):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            SELECT p.id, p.name, p.price, c.name 
            FROM products p
            JOIN categories c
            ON p.category_id = c.id
            WHERE p.id = %s
                    ''',(prod_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail='Product not found')
        return {"id": row[0], "name": row[1], "price": float(row[2]), "category": row[3]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/categories/{cate_id}/products",response_model=list[ProductOut])
def get_prod_with_cate(cate_id: int):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            SELECT p.id, p.name, p.price, c.name
            FROM products p
            JOIN categories c
            ON p.category_id = c.id
            WHERE c.id = %s        
                    ''',(cate_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            raise HTTPException(status_code=404, detail="No product in category")
        return [{"id": row[0], "name": row[1], "price": float(row[2]), "category": row[3]} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@app.put("/products/{prod_id}",response_model=ProductOut)
def update_prod(prod_id: int, prod: ProductIn):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            UPDATE products 
            SET name = %s, price = %s, category_id = %s 
            WHERE id = %s
            RETURNING id, name, price, category_id
            ''',(prod.name,prod.price,prod.category_id,prod_id))
        row = cur.fetchone()
        conn.commit()
        if not row:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Product not found")
        cur.execute("SELECT name FROM categories WHERE id = %s",(row[3],))
        cate_name = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {"id": row[0], "name": row[1], "price": float(row[2]), "category": cate_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@app.delete("/products/{prod_id}")
def deleted_prod(prod_id: int):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            DELETE FROM products
            WHERE id = %s        
                    ''',(prod_id,))
        conn.commit()
        cur.close()
        conn.close()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": f"Product with id {prod_id} has been deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        