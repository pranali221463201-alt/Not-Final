import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
try:
    c = mysql.connector.connect(
        host=os.getenv('DB_HOST','localhost'),
        user=os.getenv('DB_USER','root'),
        password=os.getenv('DB_PASSWORD','Satyam@mysql'),
        database='chainlink_pro',
        port=int(os.getenv('DB_PORT', '3306'))
    )
    cur = c.cursor()
    cur.execute("UPDATE inventory_master SET current_stock=200 WHERE product_id='PROD001' AND warehouse_id=1")
    cur.execute("UPDATE inventory_master SET current_stock=10 WHERE product_id='PROD004' AND warehouse_id=1")
    c.commit()
    print('Stock updated to trigger warnings')
finally:
    if 'cur' in locals(): cur.close()
    if 'c' in locals(): c.close()
