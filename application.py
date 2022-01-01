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

   if  environ['PATH_INFO'] == '/': 
       
       return views.home(environ,start_response)

   elif environ['PATH_INFO'] == '/events':
       
       return eventManager.subscribe("commuterrailevents",environ, start_response)
       
          
   return views.not_found(environ, start_response)

   
             
