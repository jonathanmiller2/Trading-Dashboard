import sys, os, subprocess, time, math, requests, importlib, multiprocessing
import psycopg2
import yfinance as yf
from general_logging import print_and_log

from dotenv import load_dotenv
load_dotenv(verbose=True)





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
        
        try:
            close = df['Close'].iloc[-1]
            newest_time = df.index[-1]
        except IndexError:
            print_and_log("ERROR: No yahoo finance data for the asset %s can be found. The asset symbol may be incorrect." % (symbol,))
            continue

        try:
            cur.execute('INSERT INTO exchange_rate (timestamp, from_asset, to_asset, rate) VALUES (%s, %s, %s, %s)', (newest_time, "USD", symbol, close))
            conn.commit()

        except psycopg2.errors.UniqueViolation:
            print_and_log("ERROR: pop_db.py is trying to insert a timestamp that already exists in the table")
            conn.rollback()
            sys.exit()



algostart = time.time()

cur.execute("SELECT * FROM algo;")
algos = cur.fetchall()

def run_algo(algo):
    algo_name = str(algo[0])
    filename = os.path.dirname(os.path.realpath(__file__)) + "/algos/" + algo_name + '/' + algo_name + ".py"

    if not os.path.exists(filename):
        print_and_log("The file " + filename + " does not exist. Moving onto next algo.")
        return

    spec = importlib.util.spec_from_file_location(algo_name+"_module", filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

with multiprocessing.Pool() as p:
    p.map(run_algo, algos)

algoend = time.time()

timelog = open(os.path.dirname(os.path.realpath(__file__)) + "/logs/exec_time.log", "a")
timelog.write(str(math.trunc(algoend - algostart)) + "\n")
timelog.close()

cur.close()
conn.close()


