import csv
import os

from dotenv import load_dotenv

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

connection = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB')
)

db = connection.cursor()

f = open("books.csv")
reader = csv.reader(f)

for isbn, title, author, year in reader:
    query="INSERT INTO books (isbn, title, author, year) VALUES (%s, %s, %s, %s)"
    db.execute(query,(isbn, title, author, year,))
    print("cargando")

# Commit de transacciones
connection.commit()

# Cerrar conexión
db.close()
connection.close()
