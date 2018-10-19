from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

# Authenticate credentials
URL = "https://auth.mediamath.com/"
AUTHENTICATE_URL = URL + "oauth/token"
AUDIENCE = "https://api.mediamath.com/"

CLIENT_ID = "IBxiUniDVrRYSdSXUHJgoq6KdJ7F5oN0"
CLIENT_SECRET = "NnU9qtfRtruQypo7e2QJh_as_HjlDjppZAhBP0wWeRkqdSzcVrZSln_8PdXrOn50"

def authenticate():
    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=AUTHENTICATE_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    return token

token = authenticate()