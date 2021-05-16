import os, random, argparse
import psycopg2

from dotenv import load_dotenv
load_dotenv(verbose=True)

sqlhost = os.environ.get('SQL_HOST')
sqldb = os.environ.get('SQL_DATABASE')
sqlusr = os.environ.get('SQL_USER')
sqlpass = os.environ.get('SQL_PASSWORD')
sqlport = os.environ.get('SQL_PORT')

conn = psycopg2.connect(host=sqlhost, database=sqldb, user=sqlusr, password=sqlpass, port=sqlport)
cur = conn.cursor()

cur.execute("INSERT INTO Algo (name) VALUES (%s) ON CONFLICT DO NOTHING;", ("RAND",))
conn.commit()

parser = argparse.ArgumentParser()
parser.add_argument("asset")
asset = parser.parse_args().asset

cur.close()
conn.close()