"""
Update inventory_master suppliers to real Maharashtra/MP companies,
rename warehouses to Main/Smaller Manufacturing Units.
"""
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', 'Satyam@mysql'),
    database='chainlink_pro',
    port=int(os.getenv('DB_PORT', '3306'))
)
cur = conn.cursor()

# ── 1. Rename warehouses to Manufacturing Units ──────────────────────────
cur.execute("""
    UPDATE warehouses SET name='Mumbai Main Manufacturing Unit',
    total_capacity=15000 WHERE warehouse_id=1
""")
cur.execute("""
    UPDATE warehouses SET name='Bhopal Smaller Manufacturing Unit',
    total_capacity=8000 WHERE warehouse_id=2
""")
print("[OK] Warehouses renamed")

# ── 2. Update inventory supplier names to real Maharashtra / MP suppliers ─
# Mumbai Warehouse (id=1) → Maharashtra suppliers
suppliers_mh = {
    'PROD001': 'Reliance Industries Ltd (Jamnagar)',
    'PROD002': 'Supreme Industries (Pune)',
    'PROD003': 'Sintex Plastics (Kalyan)',
    'PROD004': 'Nilkamal Ltd (Thane)',
    'PROD008': 'Kolsite Group (Navi Mumbai)',
}
for prod, supplier in suppliers_mh.items():
    cur.execute("""
        UPDATE inventory_master SET supplier_name=%s
        WHERE product_id=%s AND warehouse_id=1
    """, (supplier, prod))

# Bhopal Warehouse (id=2) → MP suppliers
suppliers_mp = {
    'PROD001': 'Neemuch Polymers Pvt Ltd (Indore)',
    'PROD002': 'Ruchi Group (Bhopal)',
    'PROD003': 'Jabalpur Plastics Works (Jabalpur)',
    'PROD004': 'Vindhya Polyfab (Sagar)',
    'PROD008': 'MP Agro Industries (Ujjain)',
}
for prod, supplier in suppliers_mp.items():
    cur.execute("""
        UPDATE inventory_master SET supplier_name=%s
        WHERE product_id=%s AND warehouse_id=2
    """, (supplier, prod))

print("[OK] Supplier names updated to real Maharashtra/MP companies")

conn.commit()
cur.close()
conn.close()
print("[OK] All updates committed")
