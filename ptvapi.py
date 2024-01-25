import os
from dotenv import load_dotenv
import urllib.parse as urlparse
import hashlib
import hmac

load_dotenv() # load environment variables from .env file

# get user ID and API key from .env
PTV_API_ID = os.getenv('PTV_API_ID')
PTV_API_KEY = os.getenv('PTV_API_KEY')

PTV_API_BASE = 'https://timetableapi.ptv.vic.gov.au' # API base URL
PTV_API_VERSION = 'v3' # API version number

# generate the completed URL for a given API endpoint (minus the version number)
# example: generate_url('/healthcheck') -> 'https://timetableapi.ptv.vic.gov.au/v3/healthcheck?devid=1234567&signature=...'
def generate_url(query: str) -> str:
    # parse given query to add ID
    parsed_query = list(urlparse.urlparse(query))

    # add user ID to query
    params = urlparse.parse_qsl(parsed_query[4]) # .query
    params.append(('devid', PTV_API_ID))
    parsed_query[4] = urlparse.urlencode(params)

    # assemble URL
    url = '/' + PTV_API_VERSION + urlparse.urlunparse(parsed_query)
    url += '&signature=' + hmac.new(bytes(PTV_API_KEY, 'utf-8'), bytes(url, 'utf-8'), hashlib.sha1).hexdigest().upper()
    url = PTV_API_BASE + url

    return url