import os
import psycopg2

SQL_HOST = os.getenv('SQL_HOST')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SQL_PORT = os.getenv('SQL_PORT')

conn = psycopg2.connect(host=SQL_HOST, database=SQL_DATABASE, user=SQL_USER, password=SQL_PASSWORD, port=SQL_PORT)
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS randseries;")
cur.execute("CREATE TABLE randseries (id serial PRIMARY KEY, timestamp timestamp, val numeric)")

conn.commit()
cur.close()
conn.close()