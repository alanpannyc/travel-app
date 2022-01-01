import gevent.monkey; gevent.monkey.patch_all()

import gevent

from gevent.pywsgi import WSGIServer


from application import make_app



 

WSGIServer(('', 8000), make_app).serve_forever()
 
