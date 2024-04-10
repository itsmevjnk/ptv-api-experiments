import os
from dotenv import load_dotenv
import urllib.parse as urlparse
import hashlib
import hmac
import requests

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

# perform API call given the API endpoint (minus the version number) and return the status code and parsed response payload
def call(query: str, catch_error: bool = True) -> tuple[int, dict]:
    resp = requests.get(generate_url(query))
    if catch_error and resp.status_code != 200:
        raise ConnectionError(f'Unexpected status code {resp.status_code}, response content: {resp.content}')
    return (resp.status_code, resp.json())

# get route types and return them as dictionary mapping ID to type name
def get_route_types() -> dict[int, str]:
    _, resp = call('/route_types')

    return {t['route_type']: t['route_type_name'] for t in resp['route_types']} # convert to dict

# get all routes of given route type ID(s) (retrieved using get_route_types()) and return them as dictionaries mapping route ID to tuple of route num, name and status mapped to type IDs
def get_routes(types: int | list[int] | None = None) -> dict[int, dict[int, tuple[int | str | None, str, str]]]:
    # normalise to list
    if types is not list:
        types = [int(types)]
    elif types is None:
        types = []
    
    params = '&'.join([f'route_types={t}' for t in types]) # generate query parameters
    
    _, resp = call('/routes' + (('?' + params) if len(params) > 0 else '')) # append params and call API

    # go through each returned route
    result = dict()
    for r in resp['routes']:
        if result.get(r['route_type']) is None: # mapping for route type does not exist yet
            result[r['route_type']] = dict()

        # process route number
        num: str = r['route_number']
        if len(num) == 0: num = None # not numbered (e.g. train)
        elif num.isnumeric(): num = int(num)

        result[r['route_type']][r['route_id']] = (num, r['route_name'], r['route_service_status']['description']) # add route
    return result

# search route info given its number and type ID (only works for trams and buses)
# returns a tuple of route ID, route name and status, or None if nothing can be found
def search_route(num: int | str, rtype: int) -> tuple[int, str, str] | None:
    routes = get_routes(rtype) # get all routes of the specified type
    for id in routes[rtype]:
        route = routes[rtype][id] # route info
        # print(route)
        if isinstance(route[0], type(num)) and route[0] == num: return (id, route[1], route[2]) # bingo!
    return None

# get available directions of a route given its ID (generally 2) and return them as dictionaries mapping direction ID to name
def get_route_directions(route: int) -> dict[int, str]:
    _, resp = call(f'/directions/route/{route}')
    return {d['direction_id']: d['direction_name'] for d in resp['directions']} # TODO: check if directions change throughout the day (e.g. Ringwood Up services entering City Loop from Parliament or Flinders Street)

# get list of stops on a route given its route and route type IDs and optionally its direction ID (for sorting by stop sequence - may be unreliable!)
# returns list of tuple of stop ID, name and (lat, long) coordinates
def get_route_stops(route: int, type: int, direction: int | None = None) -> list[tuple[int, str, tuple[float, float]]]:
    _, resp = call(f'/stops/route/{route}/route_type/{type}' + (f'?direction_id={direction}' if direction is not None else ''))
    
    stops = resp['stops']
    # print(stops)
    if direction is not None: # sort by stop sequence
        stops = sorted(stops, key = lambda s: s['stop_sequence'])
    # print(stops)
    
    return [(s['stop_id'], s['stop_name'], (s['stop_latitude'], s['stop_longitude'], s['stop_sequence'])) for s in stops] # re-shape data and return it

# get list of runs of a route given its route and route type IDs
# returns dictionary mapping run_ref to tuple of destination name and direction ID
def get_route_runs(route: int, type: int) -> dict[str, tuple[str, int]]:
    _, resp = call(f'/runs/route/{route}/route_type/{type}')
    return {r['run_ref']: (r['destination_name'], r['direction_id']) for r in resp['runs']}

# get stopping pattern of a specified run given its run_ref and route type, sorted in chronological order (better than get_route_stops())
# returns chronologically sorted list of tuples of stop ID, name, (lat, long) coordinates and whether the stop is skipped in the run (always false if include_skipped is False - because it filters out any skipped stop)
def get_run_stops(ref: str, type: int, include_skipped: bool = True) -> list[tuple[int, str, tuple[float, float]]]:
    _, resp = call(f'/pattern/run/{ref}/route_type/{type}?expand=Stops&include_skipped_stops={'true' if include_skipped else 'false'}')
    
    # extract list of non-skipped stops mapped by ID
    resp_stops = resp['stops']
    stops_id = {int(id): (resp_stops[id]['stop_name'], (resp_stops[id]['stop_latitude'], resp_stops[id]['stop_longitude'])) for id in resp_stops}

    # create list of run stops
    stops = []
    for d in resp['departures']:
        id = d['stop_id']
        stops.append((id, stops_id[id][0], stops_id[id][1], False)) # add this stop first
        if include_skipped:
            for d_skipped in d['skipped_stops']: # then any skipped stops following it
                stops.append((d_skipped['stop_id'], d_skipped['stop_name'], (d_skipped['stop_latitude'], d_skipped['stop_longitude']), True))
    
    return stops

