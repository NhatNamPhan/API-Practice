from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg2.extensions import connection
import psycopg2
from datetime import date
app = FastAPI()

class Customer(BaseModel):
    name: str
    
class OrderIn(BaseModel):
    order_date: date
    customer_id: int
    
class OrderOut(BaseModel):
    order_id: int
    order_date: date
    customer: str

class ItemIn(BaseModel):
    order_id: int
    product_id: int
    quantity: int 

class ItemOut(BaseModel):
    item_id: int
    order_id: int
    product: str
    quantity: int 
    
class OrderItemOut(BaseModel):
    product: str
    quantity: int
    price: float
    total: float
        
class OrderDetailOut(BaseModel):
    order_id: int
    order_date: date
    customer: str
    items: list[OrderItemOut]
    order_total: float
    
class CustomerOrder(BaseModel):
    order_id: int
    order_date: date
    items: list[OrderItemOut]
    order_total: float
    
class CustomerDetailOrder(BaseModel):
    customer_id: int
    customer: str
    orders: list[CustomerOrder]
    
DB_CONFIG = {
    'host': 'localhost',
    'database': 'DB_API',
    'user': 'postgres',
    'password': '1234'
}   

def get_db() -> connection:
    return psycopg2.connect(**DB_CONFIG)
 
@app.post("/orders", response_model=OrderOut)
def add_order(order: OrderIn):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (order_date, customer_id) VALUES (%s, %s) RETURNING order_id",
            (order.order_date, order.customer_id)
        )
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=400, detail="Failed to insert order")
        order_id = result[0]
        cur.execute("SELECT name FROM customers WHERE customer_id = %s", (order.customer_id,))
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Customer not found")
        customer_name = result[0]
        conn.commit()
        cur.close()
        conn.close()
        return {
            "order_id": order_id,
            "order_date": order.order_date,
            "customer": customer_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/item", response_model=ItemOut)
def add_item(item: ItemIn):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO order_items(quantity, product_id, order_id) 
            VALUES (%s, %s, %s) RETURNING item_id
                    ''',(item.quantity, item.product_id, item.order_id))
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=400, detail="Failed to insert item")
        item_id = result[0]
        cur.execute("SELECT name FROM products WHERE id = %s",(item.product_id,))
        product_name = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {
            "item_id": item_id,
            "order_id": item.order_id,
            "product": product_name,
            "quantity": item.quantity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/orders/{order_id}",response_model=OrderDetailOut)
def get_order(order_id: int):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            SELECT o.order_id, o.order_date, c.name AS customer, p.name AS product, oi.quantity, p.price,
                (oi.quantity * p.price) AS total
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.order_id = %s         
                    ''',(order_id,))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="Order not found")
        order_id, order_date, customer = rows[0][0], rows[0][1], rows[0][2]
        items = [
            {
                "product": row[3],
                "quantity": row[4],
                "price": float(row[5]),
                "total": float(row[6])
            }
            for row in rows
        ]
        order_total = sum(item['total'] for item in items)
        cur.close()
        conn.close()
        return {
            "order_id": order_id,
            "order_date": order_date,
            "customer": customer,
            "items": items,
            "order_total": order_total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@app.get("/customers/{customer_id}/orders",response_model=CustomerDetailOrder)
def customer_order(customer_id: int):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            SELECT c.customer_id, c.name AS customer, o.order_id, o.order_date, p.name AS product, 
			        oi.quantity, p.price, (oi.quantity * p.price) AS total
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON oi.product_id = p.id
            WHERE c.customer_id = %s
            ORDER BY order_id             
                    ''',(customer_id,))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="Customer not found")
        customer_id, name, = rows[0][0], rows[0][1]
        orders_dict = {}
        for row in rows:
            order_id = row[2]
            if order_id not in orders_dict:
                orders_dict[order_id] = {
                    "order_id": order_id,
                    "order_date": row[3],
                    "items": [],
                    "order_total": 0.0
                }
            item = {
                "product": row[4],
                "quantity": row[5],
                "price": float(row[6]),
                "total": float(row[7])
            }
            orders_dict[order_id]['items'].append(item)
            orders_dict[order_id]['order_total'] += item['total']
        orders = list(orders_dict.values())
        cur.close()
        conn.close()
        return {
            "customer_id": customer_id,
            "customer": name,
            "orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM orders WHERE order_id = %s",(order_id,))
        conn.commit()
        cur.close()
        conn.close()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message:": f"Order with id {order_id} has been deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        


