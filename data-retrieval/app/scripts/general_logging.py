from datetime import datetime

def print_and_log(s):
    mainlog = open("./logs/main.log", "a")
    mainlog.write("%s: %s\n" % (datetime.now(), s))
    print(s)
    mainlog.close()