import os
import psycopg2
import requests
import yfinance as yf
import pandas as pd

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
yticker = yf.Ticker(symbol)
df = yticker.history(period='1d', interval='1m')
close = df['Close'].iloc[-1]
newest_time = df.index[-1]

try:
    cur.execute(f'INSERT INTO ticker(timestamp, symbol, val) VALUES (%s, %s, %s)', (newest_time, symbol, close))
    print(f"Inserted new value:\t{newest_time}\t{close}")
    conn.commit()

except psycopg2.errors.UniqueViolation:
    print("ERROR: pop_db.py is trying to insert a timestamp that already exists in the table!")

cur.close()
conn.close()