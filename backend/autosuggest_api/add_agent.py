from werkzeug.security import generate_password_hash
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='2378',
    database='rasa_chatbot'
)
cursor = conn.cursor()

hashed_password = generate_password_hash('acer')  

cursor.execute("""
    INSERT INTO agent_login_details (agent_id, agent_name, email, password)
    VALUES (%s, %s, %s, %s)
""", ('ADMIN001', 'Acer', 'acer@cfsd.com', hashed_password))

conn.commit()
conn.close()

print("Agent Added Successfully!")
