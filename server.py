import gevent.monkey; gevent.monkey.patch_all()

import gevent

from gevent.pywsgi import WSGIServer


from application import make_app
from model import EventManager


 
eventManger=EventManager()



settings = {}

WSGIServer(('', 8000), make_app).serve_forever()
 
