import os
import psycopg2

from dotenv import load_dotenv
load_dotenv(verbose=True)

sqlhost = os.environ.get('SQL_HOST')
sqldb = os.environ.get('SQL_DATABASE')
sqlusr = os.environ.get('SQL_USER')
sqlpass = os.environ.get('SQL_PASSWORD')
sqlport = os.environ.get('SQL_PORT')

print('Connecting to DB with following parameters:')
print('HOST=' + sqlhost)
print('SQL_DB=' + sqldb)
print('USER=' + sqlusr)
print('PW=' + sqlpass)
print('PORT=' + sqlport)

conn = psycopg2.connect(host=sqlhost, database=sqldb, user=sqlusr, password=sqlpass, port=sqlport)
cur = conn.cursor()

sql_file = open('create_db.sql','r')
cur.execute(sql_file.read())

conn.commit()
cur.close()
conn.close()