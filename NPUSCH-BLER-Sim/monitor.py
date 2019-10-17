import sqlite3
import inspect, os
import shutil
import time
import datetime

rootdir=os.path.dirname( inspect.getfile(inspect.currentframe()))
db="test.db"
dbname=os.path.join(rootdir,db)
dbclone=os.path.join("/tmp",db)

total=14*8*8*501
while True:
    shutil.copy(dbname,dbclone)
    conn=sqlite3.connect(dbclone,isolation_level=None)
    monitor_statement="select finished,count(*) from BLERSIMU group by finished"
    c=conn.cursor()
    c.execute(monitor_statement)
    print datetime.datetime.now()
    for row in c:
        k= float(int(row[1]))/total*100
        print row,k
    conn.close()
    time.sleep(60)
