import gevent

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


   
    
def home_commuter_rail(environ, start_response):
   
    rawOutput="""<!DOCTYPE html>
            <html>
              <head>
                 <meta charset="utf-8" />
              </head>
              <body>

                <script>
                   var source = new EventSource('/commuterrailevents');
                   source.onmessage = function(e) {
                     document.body.innerHTML = '<h1>North Station</h1><br><h3>Massachusetts Bay Transit Authority Commuter Rail</h3><br>'+ e.data + '<br>';
                   };
                </script>
              </body>
            </html>"""  
              
    rawOutputBytes= bytes(  rawOutput ,encoding='utf-8'  )
    
    length=len(rawOutputBytes)
    
    start_response('200 OK', [('content-type','text/html'),])
                                    
   
    yield rawOutputBytes

    
def home_subway(environ, start_response):
   
    rawOutput="""<!DOCTYPE html>
            <html>
              <head>
                 <meta charset="utf-8" />
              </head>
              <body>

                <script>
                   var source = new EventSource('/subwayevents');
                   source.onmessage = function(e) {
                     document.body.innerHTML = '<h1>North Station</h1><br><h3>Massachusetts Bay Transit Authority Subway</h3><br>'+ e.data + '<br>';
                   };
                </script>
              </body>
            </html>"""  
              
    rawOutputBytes= bytes(  rawOutput ,encoding='utf-8'  )
    
    length=len(rawOutputBytes)
    
    start_response('200 OK', [('content-type','text/html'),])
                                    
   
    yield rawOutputBytes

