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
cur.execute('DROP TABLE IF EXISTS randseries;')
cur.execute('CREATE TABLE randseries (id serial PRIMARY KEY, timestamp timestamp, val numeric)')

conn.commit()
cur.close()
conn.close()