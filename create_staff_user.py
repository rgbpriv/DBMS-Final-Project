import bcrypt
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="restaurant_user",  
    password="password123",  
    database="restaurant_db"
)

# Staff credentials
name = "Alice Manager"
username = "alice"
password = "password123"
role = "Manager"

# Hash the password
hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Insert into DB
cursor = db.cursor()
cursor.execute("""
    INSERT INTO restaurant_staff (name, username, password, role)
    VALUES (%s, %s, %s, %s)
""", (name, username, hashed_pw, role))
db.commit()
cursor.close()
print("✅ Staff user created with hashed password.")
