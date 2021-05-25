from datetime import datetime, timedelta
import os

def print_and_log(s):
    mainlog = open(os.path.dirname(os.path.realpath(__file__)) + "/logs/main.log", "a+")
    mainlog.write("%s: %s\n" % (datetime.now()-timedelta(hours=5), s))
    print(s)
    mainlog.close()