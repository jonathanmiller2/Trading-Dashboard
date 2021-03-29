import os
import psycopg2
import requests

from dotenv import load_dotenv
load_dotenv(verbose=True)

from datetime import datetime
from random import random

sqlhost = os.environ.get('SQL_HOST')
sqldb = os.environ.get('SQL_DATABASE')
sqlusr = os.environ.get('SQL_USER')
sqlpass = os.environ.get('SQL_PASSWORD')
sqlport = os.environ.get('SQL_PORT')
avkey = os.environ.get('ALPHA_VANTAGE_API_KEY')

#print('Connecting to DB with following parameters:')
#print('HOST=' + sqlhost)
#print('SQL_DB=' + sqldb)
#print('USER=' + sqlusr)
#print('PW=' + sqlpass)
#print('PORT=' + sqlport)

conn = psycopg2.connect(host=sqlhost, database=sqldb, user=sqlusr, password=sqlpass, port=sqlport)
cur = conn.cursor()

symbol = "GME"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&outputsize=compact&apikey={avkey}"
response = requests.get(url).json()
value = list(response['Time Series (1min)'].values())[0]['4. close']

cur.execute(f'INSERT INTO ticker_{symbol}(timestamp, val) VALUES (%s, %s)', (datetime.now(), value))

print("Inserted new value")

conn.commit()
cur.close()
conn.close()