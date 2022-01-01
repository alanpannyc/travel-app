import gevent
from gevent.queue import Queue, Empty
import simplejson as json
from gevent.event import Event
import model
import views
import datetime
import logging

def not_found(environ, start_response):
  
    rawOutput="""<html><h1>Page not Found</h1><p>
               That page is unknown.Only urls supported are "/" and "/events" </p>
               </html>"""
        
    rawOutputBytes= bytes(  rawOutput ,encoding='utf-8'  )
    
    length=len(rawOutputBytes)
    
    start_response('404 Not Found', [('content-type','text/html'),])
                                    
  
    yield rawOutputBytes


  
def subscriber(environ, start_response):
    logging.debug ("VIEWS SUBSCRIBER environ="+str(environ))
    
    status = '200 OK'
  
    
    headers = [('Content-Type', 'text/event-stream'),
               ('Cache-Control', 'no-cache'),
               ( 'Connection', 'keep-alive' ),
               ]
            
  
    start_response(status, headers)
  
    while True:
        try:

            rawOutput=""        
            
            
            
            model.EventManager.lock.acquire(blocking=True, timeout=None)
            
            for row in model.EventManager.finalResultForDisplay:
              
              rawOutput=rawOutput+str(  row ) +"<br>"           

            model.EventManager.lock.release()
              
            

            
            yield bytes("retry: 3000\n"+ "data: %s\n\n" % json.dumps( rawOutput) ,encoding='utf-8'  )
         

            model.EventManager.event.clear()
            
            model.EventManager.event.wait()
            
    

        except Exception:
            pass
    
def home(environ, start_response):
   
    rawOutput="""<!DOCTYPE html>
            <html>
              <head>
                 <meta charset="utf-8" />
              </head>
              <body>

                <script>
                   var source = new EventSource('/events');
                   source.onmessage = function(e) {
                     document.body.innerHTML = e.data + '<br>';
                   };
                </script>
              </body>
            </html>"""  
              
    rawOutputBytes= bytes(  rawOutput ,encoding='utf-8'  )
    
    length=len(rawOutputBytes)
    
    start_response('200 OK', [('content-type','text/html'),])
                                    ### ('content-length',str(length) ),('char-set','utf-8')])
   
    yield rawOutputBytes

