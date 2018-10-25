from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import variables

# Authenticate credentials
URL = "https://auth.mediamath.com/"
AUTHENTICATE_URL = URL + "oauth/token"
AUDIENCE = "https://api.mediamath.com/"

CLIENT_ID = "IBxiUniDVrRYSdSXUHJgoq6KdJ7F5oN0"
CLIENT_SECRET = "NnU9qtfRtruQypo7e2QJh_as_HjlDjppZAhBP0wWeRkqdSzcVrZSln_8PdXrOn50"

login = None
password = None

def callAPI(platform, function, file_path):
    if function == "Test":
        authenticate()

def authenticate():
    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)
    print(variables.login_credentials)
    global username; username = variables.login_credentials['MediaMath']['Login']
    global password; password = variables.login_credentials['MediaMath']['PW']
    token = oauth.fetch_token(token_url=AUTHENTICATE_URL, username=username, password=password, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    print(token)
    return token

# token = authenticate()