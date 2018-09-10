from platforms import *

def callAPI(platform, function, file_path):
    output = {"message":"Platform not found"}

    if platform == "The Trade Desk":
        output = ttd.callAPI(function, file_path)
    elif platform == "AppNexus":
        output = appnexus.callAPI(function, file_path)
        
    return output