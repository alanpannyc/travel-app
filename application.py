import gevent
from gevent.queue import Queue, Empty
import simplejson as json
from gevent.event import Event
import model
import views


from model import EventManager
 
eventManager=EventManager()

eventManager.publishAll()
 

def make_app(environ, start_response): 
 try:
   if  environ['PATH_INFO'] == '/commuterrail': 
       
       return views.home_commuter_rail(environ,start_response)

   elif  environ['PATH_INFO'] == '/subway': 
       
       return views.home_subway(environ,start_response)

   elif environ['PATH_INFO'] == '/commuterrailevents':
    
       status = '200 OK'
  
    
       headers = [('Content-Type', 'text/event-stream'),
               ('Cache-Control', 'no-cache'),
               ( 'Connection', 'keep-alive' ),
               ]
            
  
       start_response(status, headers)
       
       return eventManager.subscribe("commuterrailevents",environ, start_response)

   elif environ['PATH_INFO'] == '/subwayevents':
    
       status = '200 OK'
  
    
       headers = [('Content-Type', 'text/event-stream'),
               ('Cache-Control', 'no-cache'),
               ( 'Connection', 'keep-alive' ),
               ]
            
  
       start_response(status, headers)
       
       return eventManager.subscribe("subwayevents"  ,environ, start_response)
       
          
   return views.not_found(environ, start_response)

 except BaseException as ex:
    import sys
    import config
    import logging
    import traceback

    logging.error("Exception caught:"+str(sys.exc_info() )  )
    logging.error(traceback.format_exc())
          
    return views.not_found(environ, start_response)
    
   
             
