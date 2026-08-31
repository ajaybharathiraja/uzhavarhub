import MySQLdb

try:
    db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root")
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS uzhavarhub")
    db.close()
    print("Database created successfully")
except Exception as e:
    print(f"Error: {e}")
