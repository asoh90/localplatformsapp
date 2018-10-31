import requests

# Authenticate credentials
AUTHENTICATE_URL = "https://auth.mediamath.com/oauth/token"
URL = "https://api.mediamath.com/"
API_URL = URL + "api/v2.0/"
SESSION_URL = API_URL + "session"

CLIENT_ID = "IBxiUniDVrRYSdSXUHJgoq6KdJ7F5oN0"
CLIENT_SECRET = "NnU9qtfRtruQypo7e2QJh_as_HjlDjppZAhBP0wWeRkqdSzcVrZSln_8PdXrOn50"



def callAPI(platform, function, file_path):
    if function == "Test":
        authenticate()

def authenticate():
    username = variables.login_credentials['MediaMath']['Login']
    password = variables.login_credentials['MediaMath']['PW']
    access_token = None

    auth_request = requests.post(AUTHENTICATE_URL,
                        headers={
                                'Content-Type':'application/json'
                        },
                        json={
                              'grant_type':'password',
                              'username':username,
                              'password':password,
                              'audience':URL,
                              'scope':"",
                              'client_id':CLIENT_ID,
                              'client_secret':CLIENT_SECRET
                        })
    print("Authenticate URL: {}".format(auth_request.url))

    if auth_request.status_code == 200:
        auth_response = auth_request.json()
        access_token = auth_response["access_token"]
    return access_token

def get_session(access_token):
    adama_session = None
    session_request = requests.get(SESSION_URL,
                        headers={
                            'Authorization':'Bearer ' + access_token,
                        })
    print("Session URL: {}".format(session_request.url))

    if session_request.status_code == 200:
        session_cookies = session_request.cookies
        session_dict = session_cookies.get_dict()
        adama_session = session_dict["adama_session"]

    return adama_session
