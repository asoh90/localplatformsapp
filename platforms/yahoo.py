import json
import variables
import requests
import write_excel
import pandas as pd
import os
import sys

topdir = os.path.join(os.path.dirname(__file__),".")
sys.path.append(topdir)
from requests_oauthlib import OAuth1

# Login credentials
key = None
secret = None
SIGNATURE_HMAC = "HMAC-SHA1"

# URL
URL = "https://datax.yahooapis.com/v1/taxonomy"

# Global output file
output = None

def callAPI(function, file_path):
    try:
        global key; key = variables.login_credentials['Yahoo']['Key']
        global secret; secret = variables.login_credentials['Yahoo']['Secret']
        # print("Key: {}".format(key))
        # print("Secret: {}".format(secret))
    except:
        return {"message":"ERROR: Incorrect login credentials! Please download 'asoh-flask-deploy.sh' file from <a href='https://eyeota.atlassian.net/wiki/pages/viewpageattachments.action?pageId=127336529&metadataLink=true'>Confluence</a> again!>"}

    output = "ERROR: option is not available"
    if (function == "Query"):
        output = get_query_all()
    else:
        output = read_file(file_path, function)
    return output

# Authenticate using oauthlib
def authenticate():
    global key
    global secret
    oauth = OAuth1(key, 
                        client_secret=secret,
                        signature_method=SIGNATURE_HMAC)
    return oauth

def read_child_segment(parent_segment, json_file):
    global output
    if "id" in json_file:
        if "description" in json_file:
            output.append(json_file['id'] + "|" + parent_segment + "|" + json_file['description'])
        else:
            output.append(json_file['id'] + "|" + parent_segment + "|")

    if "subTaxonomy" in json_file:
        child_segment_list = json_file["subTaxonomy"]
        for child_segment in child_segment_list:
            read_child_segment(parent_segment + " - " + child_segment['name'], child_segment)

def get_query_all():
    global output; output = []
    write_name = []
    write_description = []
    write_id = []

    try:
        oauth = authenticate()
        if (oauth == None):
            return{'message':"ERROR: authenticating Yahoo API. Please check .sh file if credentials are correct."}
        request_to_send = requests.get(url=URL,
                        auth=oauth)
        print("Query Request: " + request_to_send.url)
        query_response = request_to_send.json()

        for segment in query_response:
            read_child_segment(segment['name'], segment)

        for row in output:
            output_list = row.split("|")
            write_id.append(output_list[0])
            write_name.append(output_list[1])
            write_description.append(output_list[2])

        write_df = pd.DataFrame({
            "Segment ID":write_id,
            "Segment Name":write_name,
            "Segment Description":write_description
        })

        return write_excel.write(write_df, "DONOTUPLOAD_Yahoo_" + "Query")
    except:
        return {"message":"ERROR Processing Yahoo get_query_all function"}
