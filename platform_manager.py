import ttd

def callAPI(platform, function):
    if platform == "The Trade Desk":
        if (function == "query"):
            return ttd.getAuthenticationCode()
        
    return ""