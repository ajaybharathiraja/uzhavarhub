import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(marketplace_category)")
print("Category:", cursor.fetchall())
