from database import get_connection

print("Starting database connection test...")

try:
    connection = get_connection()

    print("Connection object created!")

    if connection.is_connected():
        print("DATABASE CONNECTED SUCCESSFULLY!")

    connection.close()

    print("Database connection closed.")

except Exception as e:
    print("DATABASE CONNECTION FAILED!")
    print("Error:", e)