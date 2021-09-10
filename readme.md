
probably reqiures python 3.6+

`pip install hjson requests`

go to https://app.box.com/developers/console

create a new app and select custom app

select the "Standard OAuth 2.0 (User Authentiaction)" authentication method

set the oauth 2.0 redirect url to "http://127.0.0.1:5000/return"

create `auth_data.hjson`
```hjson
{
  client_id: <client_id>
  client_secret: <client_secret>
  redirect_url: http://127.0.0.1:5000/return
}
```

run `python auth.py` and go to the generated url in a browser, enter box login

after getting redirected copy the code url param and put it into auth_data.hjson
```hjson
auth_code: <code>
```

run `python get_session.py`

run `python compare.py <box folder id> <local path>`
