import os
import psycopg2
from datetime import datetime
from random import random

SQL_HOST = os.getenv('SQL_HOST')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SQL_PORT = os.getenv('SQL_PORT')

conn = psycopg2.connect(host=SQL_HOST, database=SQL_DATABASE, user=SQL_USER, password=SQL_PASSWORD, port=SQL_PORT)
cur = conn.cursor()
cur.execute("INSERT INTO randseries(timestamp, val) VALUES (%s, %s)", (datetime.now(), random()*100)))

conn.commit()
cur.close()
conn.close()