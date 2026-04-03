import mysql.connector
import os
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'Satyam@mysql'),
        database=os.getenv('DB_NAME', 'chainlink_pro'),
        port=int(os.getenv('DB_PORT', '3306'))
    )

def seed_inventory():
    conn = get_connection()
    cursor = conn.cursor()
    
    products = ['PROD001', 'PROD002', 'PROD003', 'PROD004', 'PROD008']
    warehouses = [1, 2]
    
    print("Seeding inventory_master...")
    try:
        for p in products:
            for w in warehouses:
                stock = random.randint(50, 5000)
                lead_time = random.randint(3, 15)
                supplier = f'Supplier {random.choice(["A", "B", "C"])}'
                
                cursor.execute("""
                    INSERT INTO inventory_master 
                    (product_id, warehouse_id, current_stock, lead_time, supplier_name)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    current_stock = VALUES(current_stock), 
                    lead_time = VALUES(lead_time), 
                    supplier_name = VALUES(supplier_name)
                """, (p, w, stock, lead_time, supplier))
        conn.commit()
        print("Successfully seeded inventory_master!")
    except Exception as e:
        print(f"Error seeding inventory: {e}")
    finally:
        cursor.close()
        conn.close()

def seed_route_optimization():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Seeding route_fulfillment_plan...")
    try:
        # Generate some mock orders
        for order_idx in range(1, 6):
            order_id = f"ORD-{1000 + order_idx}"
            status = random.choice(["FULLY_FULFILLED", "PARTIALLY_FULFILLED"])
            
            for item_idx in range(random.randint(1, 4)):
                product_id = f'PROD00{random.randint(1, 8)}'
                warehouse_id = random.choice([1, 2, 3])
                allocated = random.randint(10, 500)
                dist = round(random.uniform(5.0, 500.0), 2)
                cost = round(dist * 0.5, 2)
                reason = "Optimal allocation based on distance and stock availability."
                
                cursor.execute("""
                    INSERT INTO route_fulfillment_plan 
                    (order_id, product_id, warehouse_id, allocated_quantity, distance_km, transport_cost, decision_reason, fulfillment_status, shortage_quantity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (order_id, product_id, warehouse_id, allocated, dist, cost, reason, status, 0))
        
        conn.commit()
        print("Successfully seeded route_fulfillment_plan!")
    except Exception as e:
        print(f"Error seeding route optimization: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_inventory()
    seed_route_optimization()
