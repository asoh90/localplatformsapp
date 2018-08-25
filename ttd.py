import requests

# API URL address
URL_AUTHENTICATION = "https://api.thetradedesk.com/v3/authentication"
URL_CREATE = "https://api.thetradedesk.com/v3/thirdpartydata"
URL_EDIT = "https://api.thetradedesk.com/v3/thirdpartydata"
URL_QUERY = "https://api.thetradedesk.com/v3/thirdpartydata/query"

# Login credentials
LOGIN = "dataops@eyeota.com"
PASSWORD = "Dat@ops1"

# Provider ID
PROVIDER_ID = "eyeota"

def getAuthenticationCode():
    auth_code = None
    auth_data = requests.post(URL_AUTHENTICATION,
                    headers={
                        'Content-Type':'application/json'
                    },
                    json={
                        'Login':LOGIN,
                        'Password':PASSWORD,
                        'TokenExpirationInMinutes':3600
                    }).json()
    
    # to handle invalid credentials in the future
    if auth_code is None:
        return("ERROR: getting TTD Auth Code. Please check <b>ttd.py</b> if credentials are correct.")
    
    auth_code = auth_data["Token"]
    return auth_code