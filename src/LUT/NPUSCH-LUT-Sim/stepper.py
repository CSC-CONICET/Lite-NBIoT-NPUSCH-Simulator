#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 14:24:27 2018

@author: jzuloaga

Make sure to have  MATLAB Engine API for Python Installed
cd "matlabroot/extern/engines/python"
python setup.py install
"""

import inspect, os
import sqlite3
from Queue import Queue,Empty
from threading import Thread, Event, Lock
import matlab.engine
import logging
# add filemode="w" to overwrite




####################################
NTHREADS = 8
###################################


rootdir=os.path.dirname( inspect.getfile(inspect.currentframe()))

logging.basicConfig(filename=os.path.join(rootdir,"sample.log"),
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())
#logging.debug("This is a debug message")
#logging.info("Informational message")
#logging.error("An error has happened!")

class Worker(Thread):
    NIMCS=14  #(0..10)
    NIREP=8   # (0..7)
    NIRU=8    #(0..7)
#    NISNR=101 #(0..100) #SNR = -30+ISNR*0    
    NISNR=121 #(0..100) #SNR = -35+ISNR*0    
    MONO=True
    NRU=(1,2,3,4,5,6,8,10)

    def __init__(self,id,dbname,queue,stop_event, mutex, timeout):
      #global
      self._id=id
      self._log=logging.getLogger("Wrkr%02i" % id)               
      
      #Daemon stuff
      super(Worker, self).__init__()
      self._q = queue
      self._stopper = stop_event
      self._mutex = mutex
      self._timeout=timeout
      self.daemon = True
      self.start()      
      
      
      
    def run(self):
        #SQL stuff
        self._conn=sqlite3.connect(dbname)
        self.eng = matlab.engine.start_matlab( "-sd %s" % rootdir )
        
        while not self._stopper.is_set():            
            try:
                data = self._q.get(timeout=self._timeout)            
            except Empty:
                continue
            
            try:
                self._do_work(data)
                self._q.task_done()
            except Exception as e:                                
                self._log.exception(e)
                self._abort()
                
        
        self.eng.quit()
        self._conn.close()        
        self._log.info("Closing")

    def _abort(self):
        self._log.info("Abort")
        self._stopper.set()
        while not self._q.empty():
            try: 
                self._q.get_nowait()
            except:
                continue
            
            self._q.task_done()
            

    def _do_work(self,data):
        with self._mutex:
            c=self._conn.cursor()
            finished_statement="select * from BLERSIMU where imcs=? and iru=? and irep=? and isnr=? and finished=0"
            c.execute(finished_statement,data)
            if c.fetchone() == None:
                return

        self._log.info("Processing IMCS:%i, IRU:%i, IREP:%i, ISNR:%i" % data)
        
        result=self.eng.pysimu(* ( list(data) + [self.MONO,] ))
        self.process_result(result)   
     
    def _enqueue(self,IMCS,IRU,IREP,ISNR):
        if not 0 <= IMCS < self.NIMCS: return
        if not 0 <= IRU < self.NIREP: return
        if not 0 <= IREP < self.NIRU: return
        if not 0 <= ISNR < self.NISNR: return

        enqueue_statement="INSERT INTO BLERSIMU (imcs,iru,irep,isnr,finished) VALUES (?,?,?,?,0);"
        c=self._conn.cursor()
        try:
            params=(IMCS,IRU,IREP,ISNR)
            c.execute(enqueue_statement,params)
            self._conn.commit()
            self._q.put(params)
            self._log.info("Enqued IMCS:%i, IRU:%i, IREP:%i, ISNR:%i" % params)
        except sqlite3.IntegrityError:
            pass #If primary key exists, element was already queued. 
            
    
    def process_result(self,result):    
        self._log.info( "Finished IMCS:%i, IRU:%i, IREP:%i, SNR:%2.1f, BLER=%.5f" % \
                       (result['IMCS'],result['IRU'],result['IREP'],result['snr'],result['bler']) )

        def strict_int(x):
            if not float(x).is_integer():
                raise ValueError('Value not integer')
            return int(x)

        def storeIter(IREP_range,ISNR_range):                                        
            for xIREP in IREP_range:
                for xISNR in ISNR_range:
                   yield result['IMCS'],result['IRU'],xIREP,xISNR,1,result['bler'],-30+xISNR*0.5,result['tbs'],2**xIREP * self.NRU[int(result['IRU'])]
            
        
        with self._mutex:
            c=self._conn.cursor()
            store_statement="INSERT OR REPLACE INTO BLERSIMU (imcs,iru,irep,isnr,finished,bler,snr,tbs,totru) VALUES (?,?,?,?,?,?,?,?,?);"               
                
            if (result['bler'] == 0 ):            
                genZeros = storeIter(range(strict_int(result['IREP']),self.NIREP), range(strict_int(result['ISNR']),self.NISNR))
                c.executemany(store_statement,genZeros)           
                            
                self._enqueue(result['IMCS'],result['IRU'],result['IREP'],result['ISNR']-1)
                self._enqueue(result['IMCS'],result['IRU'],result['IREP']-1,result['ISNR'])
        
            elif (result['bler'] == 1):
                genOnes = storeIter(range(0,strict_int(result['IREP'])+1), range(0,strict_int(result['ISNR'])+1))
                c.executemany(store_statement,genOnes)
        
                self._enqueue(result['IMCS'],result['IRU'],result['IREP'],result['ISNR']+1)
                self._enqueue(result['IMCS'],result['IRU'],result['IREP']+1,result['ISNR'])
                
            else:
                c.execute(store_statement,[result['IMCS'],result['IRU'],result['IREP'],result['ISNR'],1,result['bler'],result['snr'],result['tbs'],result['totru']])            
                
                self._enqueue(result['IMCS']+1,result['IRU'],result['IREP'],result['ISNR'])
                self._enqueue(result['IMCS']-1,result['IRU'],result['IREP'],result['ISNR'])
                self._enqueue(result['IMCS'],result['IRU']+1,result['IREP'],result['ISNR'])
                self._enqueue(result['IMCS'],result['IRU']-1,result['IREP'],result['ISNR'])
                self._enqueue(result['IMCS'],result['IRU'],result['IREP'],result['ISNR']+1)
                self._enqueue(result['IMCS'],result['IRU'],result['IREP'],result['ISNR']-1)
                
            self._conn.commit()
        

class ThreadPool(object):
    def __init__(self, dbname, num_t=8, timeout=1):
        self._q = Queue()
        self._stopper = Event()      
        self._conn=sqlite3.connect(dbname)
        self._log=logging.getLogger("Mngr")
        self._mutex=Lock()
        self._threads=[]
  
      # Create Worker Thread      
        for wrkr_id in range(num_t):
            self._threads.append(Worker(wrkr_id, dbname, self._q, self._stopper, self._mutex, timeout))
         
    def add_task(self,IMCS,IRU,IREP,ISNR):
        enqueue_statement="INSERT INTO BLERSIMU (imcs,iru,irep,isnr,finished) VALUES (?,?,?,?,0);"
        params=(IMCS,IRU,IREP,ISNR)
    
        c=self._conn.cursor()
        with self._mutex:
            try:
                c.execute(enqueue_statement,params)
                self._conn.commit()
                self._q.put(params)
                self._log.info("Enqued IMCS:%i, IRU:%i, IREP:%i, ISNR:%i" % params)
            except sqlite3.IntegrityError:
                pass #If primary key exists, element was already queued. 

    def resume(self):
        c=self._conn.cursor()       
        pending_statement="select imcs,iru,irep,isnr from BLERSIMU where finished = 0"
        for params in c.execute(pending_statement):
            self._q.put(params)
            self._log.info("Resuming IMCS:%i, IRU:%i, IREP:%i, ISNR:%i" % params)
            
     
        return not self._q.empty()
           
    def wait_complete(self):    
        self._q.join()
          
          
   
    def stop(self):
        self._stopper.set()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        self._log.info("Quitting: waiting for workers to finish")
        for wkr in self._threads:
            wkr.join()
        self._log.info("Quitting: all workers have closed") 
        
if __name__ == '__main__': 
   log=logging.getLogger("Main")
   log.info("Start")
   dbname=os.path.join(rootdir,"test.db")
   conn = sqlite3.connect(dbname)
   
   c = conn.cursor()
   create_table="""
        CREATE TABLE `BLERSIMU` ( 
                `imcs` INTEGER,
                `iru` INTEGER,
                `irep` INTEGER,
                `isnr` INTEGER,
                `finished` INTEGER,
                `bler` REAL,
                `snr` REAL,
                `tbs` INTEGER,
                `totru` INTEGER, 
                PRIMARY KEY(`imcs`,`iru`,`irep`,`isnr`) )"""                                        
   try:
       c.execute(create_table)       
       conn.commit()
   except sqlite3.OperationalError:
       pass
   
   with ThreadPool(dbname,NTHREADS,5) as pool:
       if not pool.resume():
          #hand picked seeds
          pool.add_task(0,	0, 0, (-11 +30)*2 )
          pool.add_task(2,	6, 1, (-9  +30)*2 )
          pool.add_task(3,	6, 4, (-15 +30)*2 )
          pool.add_task(4,	6, 0, (-3  +30)*2 )
          pool.add_task(5,	1, 2, (-5  +30)*2 )
          pool.add_task(6,	0, 2, (-6  +30)*2 )
          pool.add_task(7,	1, 5, (-15 +30)*2 )
          pool.add_task(8,	1, 6, (0   +30)*2 )           
       pool.wait_complete()

   log.info("Closing")
   
