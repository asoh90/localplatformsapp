import requests
import variables

# Authenticate credentials
AUTHENTICATE_URL = "https://auth.mediamath.com/oauth/token"
URL = "https://api.mediamath.com/"
API_URL = URL + "api/v2.0/"
SESSION_URL = API_URL + "session"
GET_SEGMENTS_URL = API_URL + "audience_segments"

CLIENT_ID = "IBxiUniDVrRYSdSXUHJgoq6KdJ7F5oN0"
CLIENT_SECRET = "NnU9qtfRtruQypo7e2QJh_as_HjlDjppZAhBP0wWeRkqdSzcVrZSln_8PdXrOn50"

SHEET_NAME = "MediaMath"

def callAPI(platform, function, file_path):
    if function == "Query All Segments":
        get_all_segments()

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

def get_segments(access_token, session):
    get_segments_request = requests.get(GET_SEGMENTS_URL,
                            headers={
                                'Authorization':"Bearer " + access_token,
                                'adama_session':session,
                                'Content-Type':"application/json"
                            })
    print("Get Segments URL: {}".format(get_segments_request.url))

    get_segments_response = None
    if get_segments_request.status_code == 200:
        get_segments_response = get_segments_request.content()

    print(get_segments_response)

def get_all_segments():
    access_token = authenticate()
    session = get_session(access_token)

    get_segments(access_token, session)