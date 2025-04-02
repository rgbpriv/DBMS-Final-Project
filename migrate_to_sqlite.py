import sqlite3
import mysql.connector

# Connect to your MySQL (MariaDB) database
mysql_db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_mysql_password",
    database="restaurant_db"
)
mysql_cursor = mysql_db.cursor(dictionary=True)

# Create SQLite database
sqlite_db = sqlite3.connect("restaurant.db")
sqlite_cursor = sqlite_db.cursor()

# Create tables in SQLite
sqlite_cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT
)
""")

sqlite_cursor.execute("""
CREATE TABLE IF NOT EXISTS menu_items (
    item_id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    price REAL,
    category TEXT,
    availability BOOLEAN
)
""")

sqlite_cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    total_price REAL,
    status TEXT
)
""")

sqlite_cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    item_id INTEGER,
    quantity INTEGER,
    subtotal REAL
)
""")

sqlite_cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurant_staff (
    staff_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")

sqlite_cursor.execute("""
CREATE TABLE IF NOT EXISTS staff_shifts (
    shift_id INTEGER PRIMARY KEY,
    staff_id INTEGER,
    shift_date TEXT,
    start_time TEXT,
    end_time TEXT
)
""")

# Tables to migrate
tables = [
    "customers", "menu_items", "orders",
    "order_items", "restaurant_staff", "staff_shifts"
]

# Copy data from MySQL to SQLite
for table in tables:
    mysql_cursor.execute(f"SELECT * FROM {table}")
    rows = mysql_cursor.fetchall()

    if rows:
        columns = rows[0].keys()
        placeholders = ", ".join(["?"] * len(columns))
        column_names = ", ".join(columns)
        insert_sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

        for row in rows:
            sqlite_cursor.execute(insert_sql, tuple(row[col] for col in columns))

sqlite_db.commit()
print("✅ Migration complete! Created restaurant.db")

mysql_cursor.close()
mysql_db.close()
sqlite_db.close()
