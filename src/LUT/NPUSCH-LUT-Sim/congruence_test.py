# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import sqlite3
import pandas as pd
conn = sqlite3.connect("/tmp/test2.db")
df = pd.read_sql_query("select * from blersimu where finished = 1", conn)

#k=df.groupby(["tbs","snr"]).filter(lambda x: not x.sort_values(["totru",])["bler"].is_monotonic_increasing)
#v=k["tbs"].sort_values().unique()

for pair in df.groupby(["tbs","snr","irep"]):
    sdf=pair[1]
    if sdf.shape[0]==1:
        continue    
    x=1.0    
    for bler in sdf.sort_values(["iru",])["bler"]:
      if bler > x:
          print pair
          break
      else:
          x=bler                
    


#df.groupby(["tbs","snr"]).filter(lambda x: x.)
