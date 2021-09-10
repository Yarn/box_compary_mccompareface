
import requests

from auth import client_id, client_secret, auth_data, save_auth_data

auth_code = auth_data['auth_code']

params = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'client_id': client_id,
    'client_secret': client_secret,
}

url = 'https://api.box.com/oauth2/token'

res = requests.post(url, data=params)

print(res.url)
print(res.content)

data = res.json()

auth_data['refresh_token'] = data['refresh_token']
auth_data['access_token'] = data['access_token']

save_auth_data()
