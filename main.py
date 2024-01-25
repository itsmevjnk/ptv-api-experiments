import ptvapi
import requests
import json

query = input('Enter the query you want to run: ')

url = ptvapi.generate_url(query)
print('Generated URL:', url)

response = requests.get(url)
print('Response code:', response.status_code)
print('Response body:')
print(json.dumps(response.json(), indent=4))