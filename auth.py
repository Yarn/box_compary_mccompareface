
from urllib.parse import quote

import requests
import hjson

with open('auth_data.hjson') as f:
    auth_data = hjson.load(f)

def save_auth_data():
    with open('auth_data.hjson', 'w') as f:
        hjson.dump(auth_data, f)

client_id = auth_data['client_id']
client_secret = auth_data['client_secret']

redirect_uri = auth_data['redirect_url']


auth_url = f'https://account.box.com/api/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={quote(redirect_uri)}&state=arbitrary_string'

def main():
    print(auth_url)
    
    # res = requests.get(auth_url)
    
    # print(res.content)

if __name__ == '__main__':
    main()
