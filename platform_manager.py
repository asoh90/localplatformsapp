from platforms import *

def callAPI(platform, function, file_path):
    output = {"message":"Platform not found"}

    if platform == "The Trade Desk":
        output = ttd.callAPI(function, file_path)
    # AppNexus has staging and prod environment
    elif platform == "AppNexus" or platform == "AppNexus Staging":
        output = appnexus.callAPI(platform, function, file_path)
        
    return output