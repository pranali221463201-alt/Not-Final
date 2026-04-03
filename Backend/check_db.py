import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', 'Satyam@mysql'),
    database=os.getenv('DB_NAME', 'chainlink_pro'),
    port=int(os.getenv('DB_PORT', '3306'))
)

cursor = conn.cursor(dictionary=True)

print("--- Inventory Master ---")
cursor.execute("SELECT COUNT(*) as count FROM inventory_master;")
print(cursor.fetchone())

print("--- Route Fulfillment Plan ---")
cursor.execute("SELECT COUNT(*) as count FROM route_fulfillment_plan;")
print(cursor.fetchone())

print("--- Analysis Sessions ---")
cursor.execute("SELECT * FROM analysis_sessions ORDER BY created_at DESC LIMIT 2;")
for row in cursor.fetchall():
    print(row)

print("--- Predictions ---")
cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 5;")
for row in cursor.fetchall():
    print(f"ID: {row['id']}, Product: {row['product_id']}, Demand: {row['predicted_demand']}")

cursor.close()
conn.close()
