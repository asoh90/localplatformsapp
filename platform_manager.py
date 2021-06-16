from platforms import *

def callAPI(platform, function, file_path):
    output = {"message":"Platform not found"}

    if platform == "The Trade Desk":
        output = ttd.callAPI(function, file_path)
    elif platform == "Adform":
        output = adform.callAPI(function, file_path)
    # AppNexus has staging and prod environment
    elif platform == "AppNexus" or platform == "AppNexus Staging":
        output = appnexus.callAPI(platform, function, file_path)
    # Amazon has staging and prod environment
    elif platform == "Amazon Staging" or platform == "Amazon NA" or platform == "Amazon EU" or platform == "Amazon FE":
        output = amazon.callAPI(platform,function,file_path)
    elif platform == "MediaMath":
        output = mediamath.callAPI(platform, function, file_path)
    elif platform == "Adobe AAM":
        output = adobeaam.callAPI(platform, function, file_path)
    elif platform == "Adobe AdCloud":
        output = adobeadcloud.callAPI(function, file_path)
    elif platform == "Yahoo" or platform == "Yahoo Staging":
        output = yahoo.callAPI(platform, function, file_path)
    elif platform == "All Report Platforms":
        output = all_report_platforms.get_report(function, file_path)
        
    return output