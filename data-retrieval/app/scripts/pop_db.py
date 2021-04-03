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

conn = psycopg2.connect(host=sqlhost, database=sqldb, user=sqlusr, password=sqlpass, port=sqlport)
cur = conn.cursor()

symbol = "GME"
api_time_format = "%Y-%m-%d %H:%M:%S"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&outputsize=compact&apikey={avkey}"
response = requests.get(url).json()

response_keys = list(response['Time Series (1min)'].keys())
response_times = [datetime.strptime(x, api_time_format) for x in response_keys]
newest_time = max(response_times)
close = response['Time Series (1min)'][newest_time.strftime(api_time_format)]["4. close"]

try:
    cur.execute(f'INSERT INTO ticker(timestamp, symbol, val) VALUES (%s, %s, %s)', (newest_time, symbol, close))
    print(f"Inserted new value: {close}")
    conn.commit()

except psycopg2.errors.UniqueViolation:
    print("ERROR: pop_db.py is trying to insert a timestamp that already exists in the table!")

cur.close()
conn.close()