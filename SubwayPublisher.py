import gevent.monkey
gevent.monkey.patch_socket()
  


import gevent

import simplejson as json
 
from gevent.event import Event

import urllib.request as mbtaStream
import config
from collections import defaultdict
import utils  
from datetime import datetime
import logging

try:
    from gevent.coros import BoundedSemaphore
except:
    from gevent.lock import BoundedSemaphore
import model
import application

def parsePredictedSchedules(json_result):
        
        
        for pos,val in enumerate(json_result["data"]):
 
            
              routeid= val['relationships']['route']['data']['id']
             
             
              tripid=val["id"]

              if (routeid, tripid) not in model.EventManager.schedules:
                                   
                  if val["attributes"]["departure_time"] is not None:
                       departureTime=val["attributes"]["departure_time"]
                     
                       departuretimeObj= datetime.strptime(departureTime[:19],"%Y-%m-%dT%H:%M:%S" )
                       now=datetime.now()
                       if now > departuretimeObj:
                            continue


                  
                  model.EventManager.schedules[(routeid, tripid) ].routeidAsKey=routeid
                  model.EventManager.schedules[(routeid, tripid) ].tripidAsKey=tripid
                  
                  logging.debug (  "("+str(routeid)+","+str( tripid)+") not in model.EventManager.schedules...adding stop from PREDICTIONS")
                  logging.debug ( "PREDICTIONS not found in SCHEDULES="+str(val))
                  
                   # tripnumber derived from json[data][relationships][trip][data][id] gets mapped to train number later
                  tripnumber= val['relationships']['trip']['data']['id']
                   
                  if tripnumber:      
                     model.EventManager.schedules[(routeid, tripid) ].tripnumber=tripnumber
                   

                                          
                  status=val["attributes"]["status"]
                  if status is not None:
                      model.EventManager.schedules[(routeid, tripid) ].status=status
            
                  if val["attributes"]["arrival_time"] is not None :
                  
                      model.EventManager.schedules[(routeid, tripid) ].arrivaltime=(val["attributes"]["arrival_time"] )
            
                  if val["attributes"]["departure_time"] is not None:
                          
                      model.EventManager.schedules[(routeid, tripid) ].departuretime=(val["attributes"]["departure_time"] )
              
                                          
def getTrainNumberAndDestination():                 

        ## we need to map tripnumber   to the (routeid,tripid) tuple key
        ## because we need to make a SINGLE http request for list of trip's destination
        ## multiple http requests with one trip per http request may result in error or too much latency
        tripnumberToRouteidTripid={}
        tripsurl=config.TRIPS+"?filter[id]="
        
        for (routeid, tripid) ,tripObj in model.EventManager.schedules.items():
            
             tripnumber=tripObj.tripnumber
             tripnumberToRouteidTripid[tripnumber]=( routeid, tripid  )
             tripsurl=tripsurl+str(tripnumber)+","
        
        json_result=model.EventManager.mbtaStream.getData(tripsurl)
        for pos,val in enumerate(json_result["data"]):
            
             tripnumber=val["id"]
             ( routeid, tripid  )=tripnumberToRouteidTripid[tripnumber]
    
             model.EventManager.schedules[(routeid, tripid) ].trainnumber=val["attributes"]["name"]
    
             model.EventManager.schedules[(routeid, tripid) ].headsign=val["attributes"]["headsign"]
    


 
def findNextTripsDepartingAndDisplay( ):

        model.EventManager.finalResultForDisplay["subwayevents"]=[]
        
        #below gets up to date next departure times
        routeDepartureTimes=defaultdict(list)
        
        for (routeid,tripid) ,tripObj in model.EventManager.schedules.items():
            routeDepartureTimes[routeid].append(tripObj)
 
                   
       
        
        
        for routeid, listTripObjects in routeDepartureTimes.items():    
           orderedTripObjects=utils.orderedTripsByTimestamp(listTripObjects,config.SUBWAY_ROUTE_TYPE_PREFIX )
    
           utils.cleanUpMemory(orderedTripObjects)

           
           nextTrip,nextnextTrip=utils.findNextDepartureTime( orderedTripObjects)

           if nextTrip and nextTrip.headsign:    
              logging.debug ("routeid:"+str(routeid)+" destination:"+str(nextTrip.headsign)+  " next departure:"+str(nextTrip.departuretime)+" status:"+str(nextTrip.status))
              model.EventManager.finalResultForDisplay["subwayevents"].append( ("routeid:",routeid," destination:",nextTrip.headsign,  " next departure:",nextTrip.departuretime," status:",nextTrip.status)   )


           if  nextnextTrip and nextnextTrip.headsign :    
              logging.debug ("routeid:"+str(routeid)+ " destination:"+str(nextnextTrip.headsign)+ " next departure:"+str(nextnextTrip.departuretime)+" status:"+str(nextnextTrip.status))
              model.EventManager.finalResultForDisplay["subwayevents"].append(  ("routeid:",routeid, " destination:",nextnextTrip.headsign, " next departure:",nextnextTrip.departuretime," status:",nextnextTrip.status) )

              




    
def updateSchedule(json_result):
         
        model.EventManager.lock.acquire(blocking=True, timeout=None)

        parsePredictedSchedules(json_result)
 
           
        getTrainNumberAndDestination()

             

        findNextTripsDepartingAndDisplay()

        

        model.EventManager.lock.release()


    

def publisher():


  
    
    while True:
        try:
          import config
          json_result=model.EventManager.mbtaStream.getData(config.SUBWAY_PREDICTIONS)
          updateSchedule(json_result)
                  
            
          # the below sends signal to the reader Greenlet
         
          application.eventManager.notifyAll("subwayevents") 
        except BaseException as ex:
          import sys
          import config
          import logging
          import traceback

          logging.error("Exception caught:"+str(sys.exc_info() )  )
          logging.error(traceback.format_exc())

          
        #if there was an exception we go to sleep and retry later--same as correct case
        
        # this writer Greenlet will yield to the reader Greenlet
        gevent.sleep(config.POLLING_INTERVAL)
            
