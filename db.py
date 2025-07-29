
import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='MySql@2024!',  
            database='shopping_list_db'
        )
        if connection.is_connected():
            print("✅ Connected to MySQL database!")
            return connection
    except Error as e:
        print(f"❌ Connection failed: {e}")
        return None
