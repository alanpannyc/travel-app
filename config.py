import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
ASYNCHRONOUS_NOTIFICATION_ONLY=False
  
  
COMMUTERRAIL_PREDICTIONS='https://api-v3.mbta.com/predictions?filter[stop]=place-north&filter[route_type]=2'

SUBWAY_PREDICTIONS='https://api-v3.mbta.com/predictions?filter[stop]=place-north&filter[route_type]=0,1'


COMMUTERRAIL_SCHEDULES='https://api-v3.mbta.com/schedules?filter[stop]=place-north&filter[route_type]=2'

SUBWAY_SCHEDULES='https://api-v3.mbta.com/schedules?filter[stop]=place-north&filter[route_type]=0,1'

TRIPS='https://api-v3.mbta.com/trips/'

VEHICLES='https://api-v3.mbta.com/vehicles/'
       
STOPS='https://api-v3.mbta.com/stops/'

POLLING_INTERVAL=30

PARENT_STATION="BNT-0000"

ROUTE_TYPE_PREFIX="CR-"


SUBWAY_ROUTE_TYPE_PREFIX="prediction-"



TRIP_LIFESPAN=120 

STREAM_URL="api-v3.mbta.com"
 
API_KEY="ed3aa4403d454a92933f08747edcadcf"


STREAM_URL_SUFFIX="/predictions/?filter[stop]=place-north&filter[route_type]=2"

     
PREDICTION_HEADER="{\"data\":["
PREDICTION_TRAILER="],\"jsonapi\":{\"version\":\"1.0\"}}"
        
