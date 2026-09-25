from database import get_connection


connection = get_connection()

cursor = connection.cursor()

cursor.execute("""
    SELECT
        NOW(),
        CURRENT_TIMESTAMP(),
        @@session.time_zone,
        @@global.time_zone
""")

result = cursor.fetchone()

print("--------------------------------")
print("MYSQL TIME TEST")
print("--------------------------------")

print("NOW():", result[0])
print("CURRENT_TIMESTAMP():", result[1])
print("Session timezone:", result[2])
print("Global timezone:", result[3])

print("--------------------------------")

cursor.close()
connection.close()