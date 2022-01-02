import gevent.monkey; gevent.monkey.patch_all()

import gevent

from gevent.pywsgi import WSGIServer


from application import make_app



try: 

   WSGIServer(('', 8000), make_app).serve_forever()

   
except BaseException as ex:
    import sys
    import config
    import logging
    import traceback

    logging.error("Exception caught:"+str(sys.exc_info() )  )
    logging.error(traceback.format_exc())
             
