
from pprint import pprint
import sys

import requests
from util import get

try:
    folder = sys.argv[1]
except IndexError:
    folder = '0'

url = f'https://api.box.com/2.0/folders/{folder}/'

res = get(url)

print(res.status_code)
print(res.content)

data = res.json()
pprint(data)
print()

for entry in data['item_collection']['entries']:
    if entry['type'] != 'file':
        continue
    
    print(f"{entry['name']:<20} {entry['sha1']}")
