import gevent.monkey
gevent.monkey.patch_socket()
 

from datetime import datetime
import logging
import urllib.request as mbtaStream

import simplejson as json
import model
class MBTAStream:
    def getData(self,url):
        json_result=None
        while True:
          try:
            with mbtaStream.urlopen(url) as response:        
              result = response.read()
         
              json_result=json.loads(result)
        
              return json_result
          
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
       

# trips =list of Trip objects with Trip.departuretime as string time stamps in YYYY-MM-DDTHH:MM:SS format
def orderedTripsByTimestamp(trips, transitType):
  

  tripObjects=[]      
  for tripObj in trips:
    if tripObj is not None and tripObj.tripidAsKey is not None and tripObj.tripidAsKey.find(transitType)!=-1:
        
        if tripObj.departuretime is not None:
            tripObj.departuretime=tripObj.departuretime[:19]#truncate to nearest second

        if tripObj.arrivaltime is not None:
            tripObj.arrivaltime=tripObj.arrivaltime[:19]#truncate to nearest second
            
        if tripObj.departuretime is not None:
            tripObjects.append(tripObj)

                  
  orderedTripsByTs=sorted(tripObjects, key=lambda tripObj: datetime.strptime(tripObj.departuretime,"%Y-%m-%dT%H:%M:%S" ))

  result=[]
  for trip in  orderedTripsByTs:
      
    trip.departuretimeObj= datetime.strptime(trip.departuretime,"%Y-%m-%dT%H:%M:%S" )
    
    result.append(trip)
  return result# returns list of objects of type Trip

def cleanUpMemory(orderedTripObjects):
    
  now=datetime.now()
  
  for i in range(len( orderedTripObjects)):
    
    if orderedTripObjects[i] is not None:
      if orderedTripObjects[i].departuretimeObj is not None:
        if now>  orderedTripObjects[i].departuretimeObj:
          
           key=( orderedTripObjects[i].routeidAsKey, orderedTripObjects[i].tripidAsKey)
           
           if key in model.EventManager.schedules:
             
              del model.EventManager.schedules[key]  
              logging.debug ("utils deleted Trip at:"+str(key))
                     
           else: 
              logging.debug ("utils releaseMemory:unknown key:"+str(key))

            

        
def findNextDepartureTime( orderedTripObjects):
  
  now=datetime.now()

  nextdeparturetime=None 
  nextnextdeparturetime=None
  
  for i in range(len( orderedTripObjects)):
    
    if i==0:
      
      if now<= orderedTripObjects[i].departuretimeObj:
         nextdeparturetime= orderedTripObjects[i]

         if i+1 <= len( orderedTripObjects )-1:
           
           if orderedTripObjects[i] and  orderedTripObjects[i+1]:
              if orderedTripObjects[i].headsign!=orderedTripObjects[i+1].headsign:
                 nextnextdeparturetime= orderedTripObjects[i+1]
         
                          
         break
       
    elif i>=1:
      
      if now> orderedTripObjects[i-1].departuretimeObj and now<= orderedTripObjects[i].departuretimeObj:
         nextdeparturetime= orderedTripObjects[i]
          
         if i+1 <= len( orderedTripObjects )-1:
           
           if orderedTripObjects[i] and  orderedTripObjects[i+1]:
              if orderedTripObjects[i].headsign!=orderedTripObjects[i+1].headsign:
                   nextnextdeparturetime= orderedTripObjects[i+1]
   
           
         break
 
  return nextdeparturetime,nextnextdeparturetime

