import os, sys, random, argparse
from decimal import *
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from general_logging import print_and_log
import psycopg2

from dotenv import load_dotenv
load_dotenv(verbose=True)

ALGO_NAME = "RAND"

now = datetime.now()
#if (now.hour < 13) or (now.hour == 13 and now.minute < 30) or (now.hour > 19):
#    print_and_log('ERROR: Algo %s attempted to trade outside of market hours' % ALGO_NAME)
#    raise Exception('ERROR: Algo %s attempted to trade outside of market hours' % ALGO_NAME)

sqlhost = os.environ.get('SQL_HOST')
sqldb = os.environ.get('SQL_DATABASE')
sqlusr = os.environ.get('SQL_USER')
sqlpass = os.environ.get('SQL_PASSWORD')
sqlport = os.environ.get('SQL_PORT')
conn = psycopg2.connect(host=sqlhost, database=sqldb, user=sqlusr, password=sqlpass, port=sqlport)
cur = conn.cursor()

cur.execute("SELECT asset FROM trades_on WHERE algo=%s;", (ALGO_NAME,))
assets = cur.fetchall()

for asset in assets:   
    cur.execute("SELECT balance FROM balance WHERE algo=%s AND asset=%s ORDER BY timestamp DESC LIMIT 1;", (ALGO_NAME, "USD"))
    cash_balance = cur.fetchone()[0]

    cur.execute("SELECT balance FROM balance WHERE algo=%s AND asset=%s ORDER BY timestamp DESC LIMIT 1;", (ALGO_NAME, asset))
    asset_balance = cur.fetchone()[0]

    cur.execute("SELECT rate FROM exchange_rate where from_asset=%s AND to_asset=%s ORDER BY timestamp DESC LIMIT 1;", ("USD", asset))
    newest_rate = cur.fetchone()[0]

    r = random.random()

    if r > 0.95 and cash_balance > 0:
        #Buy asset
        amount_bought = ((cash_balance * Decimal(0.25)) / newest_rate).quantize(Decimal(1), rounding=ROUND_DOWN)

        print_and_log("Algo %s trading from dollars to %s shares of %s" % (ALGO_NAME, amount_bought, asset))

        cur.execute("CALL make_trade(%s, %s, %s, %s, %s);", (now, ALGO_NAME, "USD", asset, amount_bought))
        conn.commit()

    elif r < 0.05 and asset_balance > 0:
        #Sell asset
        amount_bought = (asset_balance * Decimal(0.25)).quantize(Decimal(1), rounding=ROUND_DOWN) * newest_rate

        print_and_log("Algo %s trading from %s shares to %s dollars" % (ALGO_NAME, asset, amount_bought))

        cur.execute("CALL make_trade(%s, %s, %s, %s, %s);", (now, ALGO_NAME, asset, "USD", amount_bought))
        conn.commit()

cur.close()
conn.close()