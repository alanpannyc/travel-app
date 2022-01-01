import gevent.monkey
gevent.monkey.patch_socket()
  


import gevent
from gevent.queue import Queue, Empty

import simplejson as json
import logging 
from gevent.event import Event

import urllib.request as mbtaStream
import config
from collections import defaultdict
import utils  
from datetime import datetime

try:
    from gevent.coros import BoundedSemaphore
except:
    from gevent.lock import BoundedSemaphore

import CommuterRailPublisher    

#
#  the Observer Design Pattern 
#
class EventManager(object):
     
    schedules=None 
    
    mbtaStream=utils.MBTAStream()
    finalResultForDisplay=[]
    lock=BoundedSemaphore(1)
    event=Event()
    
    def __init__(self):
        self.events={}        
        self.events["commuterrailevents"]=Event()

        self.events["subwayevents"]=Event()
        self.publisher=[]
        
    def publishAll(self):    
        self.publisher.append(CommuterRailPublisher.publisher)
        gevent.spawn(CommuterRailPublisher.publisher)

        
    def notifyAll(self,subject):
        
        if subject in self.events:
            
          self.events[subject].set()
        
    def subscribe(self,subject,environ, start_response ):

      logging.debug ("models SUBSCRIBE environ="+str(environ))
    
      status = '200 OK'
  
    
      headers = [('Content-Type', 'text/event-stream'),
               ('Cache-Control', 'no-cache'),
               ( 'Connection', 'keep-alive' ),
               ]
            
  
      start_response(status, headers)
                
                    

      while True:
        try:

            rawOutput=""        
                        
                                                     
            EventManager.lock.acquire(blocking=True, timeout=None)
                
                                      
            for row in EventManager.finalResultForDisplay:                              
              
              rawOutput=rawOutput+str(  row ) +"<br>"           

            EventManager.lock.release()
                 
                
            yield bytes("retry: 3000\n"+ "data: %s\n\n" % json.dumps( rawOutput) ,encoding='utf-8'  )
        
            if subject in self.events:
                   
               self.events[subject].clear()
                        
               self.events[subject].wait()
            else:
                #handle this gracefully and go to sleep
                gevent.sleep(config.POLLING_INTERVAL)
            

        except Exception:
            pass
       
  
        
class Trip:
    def __init__(self,*args,**kwargs):
        self.status="On Time"
        self.arrivaltime=None
        self.departuretime=None
        self.departuretimeObj=None
        self.departuretimeScheduled=None
        self.destination=None
        self.trainnumber=None
        self.tracknumber=None
        self.tripnumber=None
        self.vehiclenumber=None
        self.stop=None
        self.headsign=None
       
        self.routeidAsKey=None
        self.tripidAsKey=None
        self.event=Event()
        def releaseMemory():
            if self.departuretime is None:
        
                self.event.clear()
                self.event.wait(config.TRIP_LIFESPAN)
                
                # this type of Trip is useful as Prediction that updates new status or tracknumber
                # since this is immediatelly copied to schedule then we can delete
                key=(self.routeidAsKey,self.tripidAsKey)
                        
                EventManager.lock.acquire(blocking=True, timeout=None)

                if key in EventManager.schedules:
                    del EventManager.schedules[key]          
                    logging.debug ("deleted Trip at:"+str(key))
                  
                else:
                    logging.debug ("releaseMemory:key already released:"+str(key))
                            
                EventManager.lock.release()
                return
            if self.departuretime is not None:
                
              # keep checking current time to see if this Trip has already happened:  
              while True:
        
                self.event.clear()
                self.event.wait(config.TRIP_LIFESPAN)
                
                # can be a schedule or prediction at the last second when track assigned and departing
                now=datetime.now()
                self.departuretimeObj= datetime.strptime(self.departuretime[:19],"%Y-%m-%dT%H:%M:%S" )
                if now>self.departuretimeObj:
                   key=(self.routeidAsKey,self.tripidAsKey)
                                          
                   EventManager.lock.acquire(blocking=True, timeout=None)
 
                   if key in EventManager.schedules:
                     del EventManager.schedules[key]  
                     logging.debug ("deleted Trip at:"+str(key))
                     
                   else:
                      logging.debug ("releaseMemory: key already released:"+str(key))
                                          
                   EventManager.lock.release()
                   return
 
            
        gevent.spawn(releaseMemory)

EventManager.schedules=defaultdict(Trip)
