import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT count(*) FROM marketplace_product")
print("Products:", cursor.fetchall())
cursor.execute("SELECT count(*) FROM marketplace_category")
print("Categories:", cursor.fetchall())
