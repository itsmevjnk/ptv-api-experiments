import ptvapi
import json

query = input('Enter the query you want to run: ')

url = ptvapi.generate_url(query)
print('Generated URL:', url)

status, resp = ptvapi.call(query, False)
print('Response code:', status)
print('Response body:')
print(json.dumps(resp, indent=4))