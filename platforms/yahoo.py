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
url = None

# Global output file
output = None

# Add Taxo Fixed Information
EXTENSIONS = {"urnType":"testid"}
DESCRIPTION = "Eyeota Taxonomy"
GDPR_MODE = "oath_is_processor"

def callAPI(platform, function, file_path):
    try:
        global url
        global key
        global secret
        if platform == "Yahoo":
            url = "https://datax.yahooapis.com/v1/taxonomy"
            key = variables.login_credentials['Yahoo']['Key']
            secret = variables.login_credentials['Yahoo']['Secret']
        elif platform == "Yahoo Staging":
            url = "https://sandbox.datax.yahooapis.com/v1/taxonomy"
            key = variables.login_credentials['Yahoo-Staging']['Key']
            secret = variables.login_credentials['Yahoo-Staging']['Secret']
        else:
            return {"message":"ERROR: Platform '{}' is incorrect!".format(platform)}
    except:
        return {"message":"ERROR: Incorrect login credentials! Please download 'asoh-flask-deploy.sh' file from <a href='https://eyeota.atlassian.net/wiki/pages/viewpageattachments.action?pageId=127336529&metadataLink=true'>Confluence</a> again!>"}

    output = "ERROR: option is not available"
    if (function == "Add"):
        output = read_file_to_add_segments(file_path)
    elif (function == "Query"):
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
    global url
    write_name = []
    write_description = []
    write_id = []

    try:
        oauth = authenticate()
        if (oauth == None):
            return{'message':"ERROR: authenticating Yahoo API. Please check .sh file if credentials are correct."}
        request_to_send = requests.get(url=url,
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

def split_segments_to_add(segment_dict, segment_name_list, segment_id, description):
    # print("Segment Dict Length: {}".format(len(segment_dict)))
    # print(segment_name_list)
    current_segment_name = segment_name_list[0]
    segment_name_list = segment_name_list[1:]
    # print("Current Segment Name: {}".format(current_segment_name))

    # current_segment_name already in segment_dict
    if current_segment_name in segment_dict:
        # current_segment is the lowest child segment
        if len(segment_name_list) == 0:
            segment_dict[current_segment_name]["id"] = segment_id
        # current_segment_name is not the lowest child segment
        else:
            print("Current Segment Name: {}".format(current_segment_name))
            print("Segment Dict: {}".format(segment_dict[current_segment_name]))
            # current_segment_name is already a parent in segment_dict
            if "subTaxonomy" in segment_dict[current_segment_name]:
                temp_segment_dict = segment_dict[current_segment_name]["subTaxonomy"]
                segment_dict[current_segment_name]["subTaxonomy"] = split_segments_to_add(temp_segment_dict, segment_name_list, segment_id)
            else:
                temp_subTaxonomy = split_segments_to_add({}, segment_name_list, segment_id)
                segment_dict[current_segment_name]["subTaxonomy"] = temp_subTaxonomy
    # current_segment_name is not a parent in segment_dict
    else:
        # current_segment is the lowest child segment
        if len(segment_name_list) == 0:
            # print("length is zero")
            segment_dict[current_segment_name] = {"id":segment_id}
        # current_segment_name is not the lowest child segment
        else:
            # print("length is not zero")
            temp_subTaxonomy = split_segments_to_add({}, segment_name_list, segment_id)
            segment_dict[current_segment_name] = {"subTaxonomy":temp_subTaxonomy}

    return segment_dict

def format_segment_json(segment_dict):
    # {"name": "AU CoreLogic RP Data", "type": "SEGMENT", "targetable": "false", "subTaxonomy": [
        # {"name": "Real Estate Indicator", "type": "SEGMENT", "targetable": "false", "subTaxonomy": [
    # print(segment_dict)
    to_print = ""
    is_first_segment_name = True

    for segment_name in segment_dict:
        if is_first_segment_name:
            is_first_segment_name = False
        else:
            to_print = to_print + ","
        targetable = False
        # is most child segment
        if "id" in segment_dict[segment_name]:
            targetable = True
        if targetable:
            to_print = to_print + "{{\"name\": \"{}\", \"id\":\"{}\", \"gdpr_mode\":\"{}\", \"type\":\"SEGMENT\", \"targetable\":\"{}\"".format(segment_name, segment_dict[segment_name]["id"],GDPR_MODE,targetable)
        else:
            to_print = to_print + "{{\"name\": \"{}\", \"type\":\"SEGMENT\", \"targetable\":\"{}\"".format(segment_name, targetable)
        if "subTaxonomy" in segment_dict[segment_name]:
            to_print = to_print + (",\"subTaxonomy\":[")
            to_print = to_print + format_segment_json(segment_dict[segment_name]["subTaxonomy"])
            to_print = to_print + ("]}")
        else:
            to_print = to_print + ("}")
    return to_print

def read_file_to_add_segments(file_path):
    read_df = None
    try:
        read_df = pd.read_excel(file_path, sheet_name="Yahoo", skiprows=[1])
    except:
        return {"message":"File Path '{}' is not found".format(file_path)}

    segment_dict = {}
    temp_dict = None
    
    segment_name_list = read_df["Segment Name"]
    segment_id_list = read_df["Segment ID"]
    for row_num in range(len(segment_name_list)):
        segment_id = segment_id_list[row_num]
        # print("Segment Name: {}".format(segment_name_list[row_num]))
        # print("Segment ID: {}".format(segment_id_list[row_num]))
        segment_name_split = segment_name_list[row_num].split(" - ")
        segment_dict = split_segments_to_add(segment_dict, segment_name_split, segment_id)
    print(segment_dict)
    # print("[{}]".format(format_segment_json(segment_dict)))
    return {"message":"[{}]".format(format_segment_json(segment_dict))}