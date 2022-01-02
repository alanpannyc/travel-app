
import http.client as httplib
import simplejson as json
import model
import logging

import gevent



import simplejson as json
from gevent.event import Event
import urllib.request as mbtaStream
import config
from collections import defaultdict
import utils  
from datetime import datetime
import CommuterRailPublisher
import application


def publisher():
  ## this implements Server Sent Events protocol
  ## this is Asynchronous notifications from MBTA server
  ## this is retrieving Commuter Rail Events
  while True:  
    try:
      conn = httplib.HTTPSConnection(config.STREAM_URL)
  
      eventStreamHeaders={"accept": "text/event-stream" , "x-api-key": config.API_KEY}

      conn.request(method="GET", url=config.STREAM_URL_SUFFIX,headers=eventStreamHeaders)
 
      response = conn.getresponse()

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
    
    else:
     
      break

   
  i=0
  result=[]
  while True:
    try:
    
      data = response.fp.readline()
   
      result.append(str(data))
  
      if i>0:
        # if we receive updated prediction or new prediction         
        if result[i-1].find("event: update")!=-1 or result[i-1].find("event: add")!=-1:
          
            eventStart=result[i].find("{")
            eventEnd=result[i].rfind("}")
            
            prediction=eval(config.PREDICTION_HEADER  +
                            result[i][eventStart:eventEnd+1].replace("null", "None")+
                            config.PREDICTION_TRAILER  )
            
            logging.debug ("Server Sent Events PUBLISHER prediction:"+str(  result[i-1])+ str(prediction)) 
            
            CommuterRailPublisher.updateSchedule(prediction)
            
            
         
            application.eventManager.notifyAll("commuterrailevents") 


            
            gevent.sleep(config.POLLING_INTERVAL)

       
      i=i+1
    except BaseException as ex:
      import sys
      import config
      import logging
      import traceback

      logging.error("Exception caught:"+str(sys.exc_info() )  )
      logging.error(traceback.format_exc())
  

if __name__=="__main__":
    publisher() 
