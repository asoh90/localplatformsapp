import requests
import variables
import write_excel
import pandas as pd
import json

AUTH_URL = "https://dmp-api.adform.com/v1/token"
API_URL = "https://api.adform.com/v1/dmp/"

# Login credentials
username = None
password = None
CONTENT_TYPE = "application/x-www-form-urlencoded"
GRANT_TYPE = "password"

# Query all constants
CATEGORIES_URL = API_URL + "categories"
SEGMENTS_URL = API_URL + "segments"
LIMIT = 5000

def callAPI(function, file_path):
    try:
        global username; username = variables.login_credentials['Adform']['Login']
        global password; password = variables.login_credentials['Adform']['PW']
    except:
        return {"message":"ERROR: Incorrect login credentials! Please download 'asoh-flask-deploy.sh' file from <a href='https://eyeota.atlassian.net/wiki/pages/viewpageattachments.action?pageId=127336529&metadataLink=true'>Confluence</a> again!>"}

    output = {"message":"ERROR: option is not available"}

    if function == "Query All Segments":
        output = get_all_segments()

    return output

def authenticate():
    data = {
                "grant_type":GRANT_TYPE,
                "username":username,
                "password":password
            }
    auth_json = requests.post(AUTH_URL,
                            headers={
                                'Content-Type':CONTENT_TYPE
                            },
                            data=data).json()
    auth_token = auth_json["access_token"] 
    return auth_token

def get_categories(access_token):
    get_categories_request = requests.get(CATEGORIES_URL,
                                        headers={
                                            'Content-Type':'application/json',
                                            'Authorization':'Bearer ' + access_token
                                        })
    print("Get Categories URL: {}".format(get_categories_request.url))
    if not get_categories_request.status_code == 200:
        return None

    return get_categories_request.json()

def store_category_in_dict(categories_json):
    categories_dict = {}

    for category in categories_json:
        category_id = category["id"]
        category_name = category["name"]
        category_dataProviderId = category["dataProviderId"]
        category_parentId = None
        if "parentId" in category:
            category_parentId = category["parentId"]
        category_regions = category["regions"]
        category_updatedAt = category["updatedAt"]
        category_createdAt = category["createdAt"]

        categories_dict[category_id] = {"name":category_name,
                                        "dataProviderId":category_dataProviderId,
                                        "parentId":category_parentId,
                                        "regions":category_regions,
                                        "updatedAt":category_updatedAt,
                                        "createdAt":category_createdAt}
    
    return categories_dict

def get_full_category_name(parent_category_id, child_category_name, categories_dict):
    while parent_category_id in categories_dict and not parent_category_id == None:
        child_category_name = categories_dict[parent_category_id]["name"] + " - " + child_category_name
        parent_category_id = categories_dict[parent_category_id]["parentId"]
    return child_category_name

def get_segments(access_token, offset):
    get_segments_request = requests.get(SEGMENTS_URL,
                                        headers={
                                            'Content-Type':'application/json',
                                            'Authorization':'Bearer ' + access_token
                                        },
                                        params={
                                            'returnTotalCount':True,
                                            'offset':offset,
                                            'limit':LIMIT
                                        })
    print("Get Segments URL: {}".format(get_segments_request.url))
    if not get_segments_request.status_code == 200:
        return None

    headers_dict = dict(get_segments_request.headers)
    total_count = int(headers_dict["Total-Count"])
    return total_count, get_segments_request.json()

def get_all_segments():
    segment_id_list = []
    segment_dataProviderId_list = []
    segment_status_list = []
    segment_categoryId_list = []
    segment_refId_list = []
    segment_fee_list = []
    segment_ttl_list = []
    segment_name_list = []
    segment_audience_list = []
    segment_clicks_list = []
    segment_impressions_list = []

    access_token = authenticate()
    categories_json = get_categories(access_token)

    if categories_json == None:
        return {"message":"ERROR: unable to retrieve categories"}
    
    categories_dict = store_category_in_dict(categories_json)

    segment_offset = 0
    segment_total = LIMIT

    while segment_offset < segment_total:
        segment_total, segments_json = get_segments(access_token, segment_offset)

        for segment in segments_json:
            segment_id = segment["id"]
            segment_dataProviderId = segment["dataProviderId"]
            segment_status = segment["status"]
            segment_categoryId = segment["categoryId"]
            segment_refId = segment["refId"]
            segment_fee = segment["fee"]
            segment_ttl = segment["ttl"]
            segment_name = segment["name"]
            segment_audience = segment["audience"]

            segment_usageStatistics = None
            segment_clicks = None
            segment_impressions = None
            segment_rank = None
            if "usageStatistics" in segment:
                segment_usageStatistics = segment["usageStatistics"]
                segment_clicks = segment_usageStatistics["clicks"]
                segment_impressions = segment_usageStatistics["impressions"]

            category_parentId = categories_dict[segment_categoryId]["parentId"]
            category_name = categories_dict[segment_categoryId]["name"]
            category_full_name = get_full_category_name(category_parentId, category_name, categories_dict)

            segment_full_name = category_full_name + " - " + segment_name

            segment_id_list.append(segment_id)
            segment_dataProviderId_list.append(segment_dataProviderId)
            segment_status_list.append(segment_status)
            segment_categoryId_list.append(segment_categoryId)
            segment_refId_list.append(segment_refId)
            segment_fee_list.append(segment_fee)
            segment_ttl_list.append(segment_ttl)
            segment_name_list.append(segment_full_name)
            segment_audience_list.append(segment_audience)
            segment_clicks_list.append(segment_clicks)
            segment_impressions_list.append(segment_impressions)

        segment_offset += LIMIT

    write_df = pd.DataFrame({
        "Ref ID":segment_refId_list,
        "Segment Name":segment_name_list,
        "Segment Status":segment_status_list,
        "Segment Fee":segment_fee_list,
        "Segment TTL":segment_ttl_list,
        "Segment Audience":segment_audience_list,
        "Segment Clicks":segment_clicks_list,
        "Segment Impressions":segment_impressions_list,
        "Data Provider ID":segment_dataProviderId_list,
        "Category ID":segment_categoryId_list,
        "Segment ID":segment_id_list
    })
    return write_excel.write(write_df, "DONOTUPLOAD_Adform_query_all")