import os, subprocess, time, math, requests
import psycopg2
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

cur.execute("SELECT * FROM asset;")
assets = cur.fetchall()

for asset in assets:
    symbol = asset[0]
    source = asset[1]

    if(source == 'YF'):
        yticker = yf.Ticker(symbol)
        df = yticker.history(period='1d', interval='1m')
        close = df['Close'].iloc[-1]
        newest_time = df.index[-1]

        try:
            cur.execute('INSERT INTO exchange_rate (timestamp, from_asset, to_asset, rate) VALUES (%s, %s, %s, %s)', (newest_time, "USD", symbol, close))
            print(f"Inserted new value:\t{newest_time}\t{close}")
            conn.commit()

        except psycopg2.errors.UniqueViolation:
            print("ERROR: pop_db.py is trying to insert a timestamp that already exists in the table!")
            conn.rollback()



algostart = time.time()

cur.execute("SELECT * FROM algo;")
algos = cur.fetchall()

for algo in algos:
    algo_name = str(algo[0])
    filename = "./algos/" + algo_name + ".py"
    
    cur.execute("SELECT * FROM trades_on WHERE algo=%s;", (algo_name,))
    assets = cur.fetchall()

    for asset in assets:
        subprocess.run(["python", filename, asset[0]])

algoend = time.time()

f = open("exec_time.log", "a")
f.write(str(math.trunc(algoend - algostart)) + "\n")
f.close()

cur.close()
conn.close()