import gevent.monkey
gevent.monkey.patch_socket()
  


import gevent
from gevent.queue import Queue, Empty

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


def parsePredictedSchedules(json_result):
        
        
        for pos,val in enumerate(json_result["data"]):
 
            
              routeid= val['relationships']['route']['data']['id']
             
              ind= val["id"].find(config.ROUTE_TYPE_PREFIX)
              tripid=val["id"][ind:]

              if (routeid, tripid) not in model.EventManager.schedules:
                  model.EventManager.schedules[(routeid, tripid) ].routeidAsKey=routeid
                  model.EventManager.schedules[(routeid, tripid) ].tripidAsKey=tripid
                  
                  logging.debug (  "("+str(routeid)+","+str( tripid)+") not in model.EventManager.schedules...adding stop from PREDICTIONS")
                  logging.debug ( "PREDICTIONS not found in SCHEDULES="+str(val))
                  # when track number is assigned, this will update with a new record that has tripid=original tripid + parent station id+platform code(tracknumber)
                  # however it will have departure_time ==None  most of the time
                  model.EventManager.schedules[(routeid, tripid) ].stop=val['relationships']['stop']['data']['id']

                                          
              status=val["attributes"]["status"]
              if status is not None:
                  model.EventManager.schedules[(routeid, tripid) ].status=status
            
              if val["attributes"]["arrival_time"] is not None :
                  
                  model.EventManager.schedules[(routeid, tripid) ].arrivaltime=(val["attributes"]["arrival_time"] )
            
              if val["attributes"]["departure_time"] is not None:
                  if model.EventManager.schedules[(routeid, tripid) ].departuretimeScheduled is not None  :
                     olddeparturetime=model.EventManager.schedules[(routeid, tripid) ].departuretimeScheduled[:19]
                     newdeparturetime=(val["attributes"]["departure_time"][:19] )
   
                     olddeparturetimeObj= datetime.strptime(olddeparturetime,"%Y-%m-%dT%H:%M:%S" )
                     newdeparturetimeObj= datetime.strptime(newdeparturetime,"%Y-%m-%dT%H:%M:%S" )
                     if newdeparturetimeObj > olddeparturetimeObj:
                         model.EventManager.schedules[(routeid, tripid) ].status="Delayed"
                          
                  model.EventManager.schedules[(routeid, tripid) ].departuretime=(val["attributes"]["departure_time"] )
              
                                          
def getTrainNumberAndDestination():                 

        ## we need to map tripnumber and stop id  to the (routeid,tripid) tuple key
        ## because we need to make a SINGLE http request for list of trip's trainnumber
        ## multiple http requests with one trip per http request may result in error or too much latency
        tripnumberToRouteidTripid={}
        tripsurl=config.TRIPS+"?filter[id]="
        
        for (routeid, tripid) ,tripObj in model.EventManager.schedules.items():
            
             tripnumber=tripObj.tripnumber
             tripnumberToRouteidTripid[tripnumber]=( routeid, tripid  )
             tripsurl=tripsurl+str(tripnumber)+","
        
        # SCHEDULES relationships trip data id maps to TRIPS attributes name==trainnumber
        # Note: the trainnumber below is DIFFERENT from vehicle number
        
        json_result=model.EventManager.mbtaStream.getData(tripsurl)
        for pos,val in enumerate(json_result["data"]):
            
             tripnumber=val["id"]
             ( routeid, tripid  )=tripnumberToRouteidTripid[tripnumber]
    
             model.EventManager.schedules[(routeid, tripid) ].trainnumber=val["attributes"]["name"]
    
             model.EventManager.schedules[(routeid, tripid) ].headsign=val["attributes"]["headsign"]
    


def getAssigndTrackNumberFromPredictionsStopId():

        stopidToRouteidTripid={}
        stopsurl=config.STOPS+"?filter[id]="
        
        for (routeid, tripid) ,tripObj in model.EventManager.schedules.items():
           stopid=tripObj.stop
           
           stopidToRouteidTripid[stopid]=(routeid, tripid)
           
           stopsurl=stopsurl+str(stopid)+","
               
        routeidToTrackNumber={}
        
        json_result=model.EventManager.mbtaStream.getData(stopsurl)
        for pos,val in enumerate(json_result["data"]):
             
             stopid=val["id"]
             (routeid, tripid)=   stopidToRouteidTripid[stopid]
             logging.debug ("RESPONSE FROM STOPS QUERY: routeid:"+ str(routeid)+"tripid:"+str(tripid)+ "departuretime:"+str(model.EventManager.schedules[(routeid, tripid) ].departuretime)+"track number"+str(val['attributes']['platform_code']))
             
             if stopid.find(config.PARENT_STATION)!=-1:
                    
                    trainnumber=str(tripid.split("-")[2])

                    
                    model.EventManager.schedules[(routeid, tripid) ].tracknumber=val['attributes']['platform_code']
                    
                    routeidToTrackNumber[(routeid,trainnumber)]=val['attributes']['platform_code']
               
               
        return routeidToTrackNumber

 
def findNextTripsDepartingAndDisplay( routeidToTrackNumber):


        
        #below gets up to date next departure times
        routeDepartureTimes=defaultdict(list)
        
        for (routeid,tripid) ,tripObj in model.EventManager.schedules.items():
            routeDepartureTimes[routeid].append(tripObj)
 
                   
       
        model.EventManager.finalResultForDisplay=[]
        
        for routeid, listTripObjects in routeDepartureTimes.items():    
           orderedTripObjects=utils.orderedTripsByTimestamp(listTripObjects)
    
           utils.cleanUpMemory(orderedTripObjects)

           
           nextTrip,nextnextTrip=utils.findNextDepartureTime( orderedTripObjects)
           if nextTrip :
             if (routeid,str(nextTrip.trainnumber)  ) in routeidToTrackNumber:
                
                logging.debug ("adding tracknumber to Trip:"+ str( routeidToTrackNumber[(routeid , str(nextTrip.trainnumber))  ]))
                
                nextTrip.tracknumber=routeidToTrackNumber[(routeid,str(nextTrip.trainnumber)) ]

           if nextTrip and nextTrip.headsign:    
              logging.debug ("routeid:"+str(routeid)+" destination:"+str(nextTrip.headsign)+  " next departure:"+str(nextTrip.departuretime)+" status:"+str(nextTrip.status)+" trainnumber:"+str(nextTrip.trainnumber)+" tracknumber:"+str(nextTrip.tracknumber))
              model.EventManager.finalResultForDisplay.append( ("routeid:",routeid," destination:",nextTrip.headsign,  " next departure:",nextTrip.departuretime," status:",nextTrip.status," trainnumber:",nextTrip.trainnumber," tracknumber:",nextTrip.tracknumber)   )


           if  nextnextTrip :
             if (routeid,str(nextnextTrip.trainnumber)  ) in routeidToTrackNumber:
                
                logging.debug ("adding tracknumber to Trip:"+  str(routeidToTrackNumber[(routeid , str(nextnextTrip.trainnumber))  ]))
                
                nextnextTrip.tracknumber=routeidToTrackNumber[(routeid,str(nextnextTrip.trainnumber)) ]

           if  nextnextTrip and nextnextTrip.headsign :    
              logging.debug ("routeid:"+str(routeid)+ " destination:"+str(nextnextTrip.headsign)+ " next departure:"+str(nextnextTrip.departuretime)+" status:"+str(nextnextTrip.status)+" trainnumber:"+str(nextnextTrip.trainnumber)+" tracknumber:"+str(nextnextTrip.tracknumber))
              model.EventManager.finalResultForDisplay.append(  ("routeid:",routeid, " destination:",nextnextTrip.headsign, " next departure:",nextnextTrip.departuretime," status:",nextnextTrip.status," trainnumber:",nextnextTrip.trainnumber," tracknumber:",nextnextTrip.tracknumber) )

              




    
def updateSchedule(json_result):
         
        model.EventManager.lock.acquire(blocking=True, timeout=None)

        parsePredictedSchedules(json_result)
 
           
        getTrainNumberAndDestination()


        routeidToTrackNumber=getAssigndTrackNumberFromPredictionsStopId()
             

        findNextTripsDepartingAndDisplay( routeidToTrackNumber)

        

        model.EventManager.lock.release()

    
def getSchedule():
        
        
        model.EventManager.lock.acquire(blocking=True, timeout=None)
 
        
        json_result=model.EventManager.mbtaStream.getData(config.COMMUTERRAIL_SCHEDULES)
        
        for pos,val in enumerate(json_result["data"]):
  
               
              routeid= val['relationships']['route']['data']['id']
             
              ind= val["id"].find(config.ROUTE_TYPE_PREFIX)
              tripid=val["id"][ind:]

              if (routeid, tripid) not in model.EventManager.schedules:
                  if val["attributes"]["departure_time"] is not None:
                       departureTime=val["attributes"]["departure_time"]
                     
                       departuretimeObj= datetime.strptime(departureTime[:19],"%Y-%m-%dT%H:%M:%S" )
                       now=datetime.now()
                       if now > departuretimeObj:
                            continue
                        
       
                  model.EventManager.schedules[(routeid, tripid) ].routeidAsKey=routeid
                  model.EventManager.schedules[(routeid, tripid) ].tripidAsKey=tripid
             
              if val["attributes"]["departure_time"] is not None:
                
                if  val['relationships']['route']['data']['id'].find(config.ROUTE_TYPE_PREFIX)!=-1:
                   

                   # tripnumber derived from json[data][relationships][trip][data][id] gets mapped to train number later
                   tripnumber= val['relationships']['trip']['data']['id']
                   
                   if tripnumber:      
                     model.EventManager.schedules[(routeid, tripid) ].tripnumber=tripnumber
                   
                   if (val["attributes"]["departure_time"] is not None ):
                       
                     model.EventManager.schedules[(routeid, tripid) ].departuretime=(val["attributes"]["departure_time"] )

                     model.EventManager.schedules[(routeid, tripid) ].departuretimeScheduled=(val["attributes"]["departure_time"] )

                     
                   if (val["attributes"]["arrival_time"] is not None ):
                     model.EventManager.schedules[(routeid, tripid) ].arrivaltime=(val["attributes"]["arrival_time"] )
                   
        

        model.EventManager.lock.release()

    

def publisher():


  
    
    while True:
        # get static daily schedule
        getSchedule()

        
        # get predictions which are changes to schedule(updates status or departure time or
        # stop id which is same as track number
        json_result=model.EventManager.mbtaStream.getData(config.COMMUTERRAIL_PREDICTIONS)
        updateSchedule(json_result)
                  
            
        # the below sends signal to the reader Greenlet
        model.EventManager.event.set()

        # this writer Greenlet will yield to the reader Greenlet
        gevent.sleep(config.POLLING_INTERVAL)

        if config.ASYNCHRONOUS_NOTIFICATION_ONLY: 
            import BackupCommuterRailPublisher
            # the below will only query for trainnumber and tracknumber if there is asynchronous update of stop id
            # which reduces http request traffic
            BackupCommuterRailPublisher.publisher()
            
