
import requests

from auth import auth_data, save_auth_data

def do_refresh_token():
    auth_code = auth_data['auth_code']
    
    params = {
        'grant_type': 'refresh_token',
        # 'code': auth_data['auth_code'],
        'refresh_token': auth_data['refresh_token'],
        'client_id': auth_data['client_id'],
        'client_secret': auth_data['client_secret'],
    }
    
    url = 'https://api.box.com/oauth2/token'
    
    res = requests.post(url, data=params)
    
    if res.status_code != 200:
        print(res.status_code)
        print(res.content)
    
    assert res.status_code == 200
    
    auth_data['access_token'] = res.json()['access_token']
    print(auth_data['access_token'])
    save_auth_data()

def get(url, params=None, *, refresh_token=True):
    headers = {
        'Authorization': f'Bearer {auth_data["access_token"]}'
    }
    
    res = requests.get(url, params=params, headers=headers)
    
    if res.status_code == 401 and refresh_token:
        do_refresh_token()
        res = get(url, params, refresh_token=False)
    
    assert res.status_code == 200, f"Call failed {res.status_code}"
    
    return res
