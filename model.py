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
import SubwayPublisher

#
#  the Observer Design Pattern 
#
class EventManager(object):
     
    schedules=None 
    
    mbtaStream=utils.MBTAStream()
    finalResultForDisplay=defaultdict(list)
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

        self.publisher.append(SubwayPublisher.publisher)
        gevent.spawn(SubwayPublisher.publisher)

        
    def notifyAll(self,subject):
        
        if subject in self.events:
            
          self.events[subject].set()
        
    def subscribe(self,subject):

                     

      while True:
        try:

            rawOutput=""        
                        
                                                     
            EventManager.lock.acquire(blocking=True, timeout=None)
                
                                      
            for row in EventManager.finalResultForDisplay[subject]:                              
              
              rawOutput=rawOutput+str(  row ) +"<br>"           

            EventManager.lock.release()
            
            #     
            # Note that the below is actually the Server Sent Events protocol:
            #
            yield bytes("retry: 3000\n"+ "data: %s\n\n" % json.dumps( rawOutput) ,encoding='utf-8'  )
        
            if subject in self.events:
                   
               self.events[subject].clear()
                        
               self.events[subject].wait()
            else:
                #handle this gracefully and go to sleep
                logging.error("subject not found in events:"+str(subject) )
                gevent.sleep(config.POLLING_INTERVAL)
            

        
        except BaseException as ex:
              import sys
              import config
              import logging
              import traceback
              logging.error("Exception caught:"+str(sys.exc_info() )  )
              logging.error(traceback.format_exc())
              import gevent
              import config
              gevent.sleep(config.POLLING_INTERVAL)       
  
        
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
          try:
            import logging  
            if self.departuretime is None:
                import config
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
                import config
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
 
          except BaseException as ex:
              import sys
              import config
              import logging
              import traceback
              logging.error("Exception caught:"+str(sys.exc_info() )  )
              logging.error(traceback.format_exc())    
        gevent.spawn(releaseMemory)

EventManager.schedules=defaultdict(Trip)
