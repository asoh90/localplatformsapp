import requests
import variables
import write_excel
import pandas as pd
import json
import os

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

# Add all constants
SEGMENT_STATUS = "inactive"

def callAPI(function, file_path):
    try:
        global username; username = variables.login_credentials['Adform']['Login']
        global password; password = variables.login_credentials['Adform']['PW']
    except:
        return {"message":"ERROR: Incorrect login credentials! Please download 'asoh-flask-deploy.sh' file from <a href='https://eyeota.atlassian.net/wiki/pages/viewpageattachments.action?pageId=127336529&metadataLink=true'>Confluence</a> again!>"}

    output = {"message":"ERROR: option is not available"}

    if function == "Add Segments":
        output = read_file_to_add_segments(file_path)
    
    elif function == "Query All Segments":
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
        "Status":segment_status_list,
        "Fee":segment_fee_list,
        "TTL":segment_ttl_list,
        "Audience":segment_audience_list,
        "Clicks":segment_clicks_list,
        "Impressions":segment_impressions_list,
        "Data Provider ID":segment_dataProviderId_list,
        "Category ID":segment_categoryId_list,
        "Segment ID":segment_id_list
    })
    return write_excel.write(write_df, "DONOTUPLOAD_Adform_query_all")

# Add segment functions
def add_category(access_token, category_name, region, parent_category_id):
    data_provider_id = "67"
    if region.lower() == "apac":
        data_provider_id = "11399"

    add_category_json = None
    if parent_category_id == None:
        add_category_json = {
                                "Name": category_name,
                                "DataProviderId": data_provider_id,
                                "Regions": []
                            }
    else:
        add_category_json = {
                                "Name": category_name,
                                "DataProviderId": data_provider_id,
                                "ParentId": parent_category_id,
                                "Regions": []
                            }

    add_category_request = requests.post(CATEGORIES_URL,
                            headers={
                                'Content-Type':'application/json',
                                'Authorization':'Bearer ' + access_token
                            },
                            json=add_category_json)
    print("Add Category URL: {}".format(add_category_request.url))
    # print(add_category_request.json())
    if add_category_request.status_code == 201:
        add_category_response = add_category_request.json()
        return add_category_response["id"]
    else:
        return None

def add_segment(access_token, region, category_id, ref_id, fee, ttl, name):
    data_provider_id = "67"
    if region.lower() == "apac":
        data_provider_id = "11399"

    add_segment_request = requests.post(SEGMENTS_URL,
                            headers={
                                "Content-Type":"application/json",
                                "Authorization":"Bearer " + access_token
                            },
                            json={
                                "DataProviderId":data_provider_id,
                                "Status":SEGMENT_STATUS,
                                "CategoryId":category_id,
                                "RefId":str(ref_id),
                                "Fee":fee,
                                "Ttl":ttl,
                                "Name":name,
                                "Frequency":1
                            })
    print("Add Segment URL: {}".format(add_segment_request.url))

    add_segment_json = add_segment_request.json()
    # print(add_segment_json)
    if add_segment_request.status_code == 201:
        segment_id = add_segment_json["id"]
        return 201, segment_id
    else:
        return None, add_segment_json["params"]

def store_category_in_dict_by_name(categories_json):
    child_category_dict = {}
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

        child_category_dict[category_id] = {"name":category_name,
                                        "dataProviderId":category_dataProviderId,
                                        "parentId":category_parentId,
                                        "regions":category_regions,
                                        "updatedAt":category_updatedAt,
                                        "createdAt":category_createdAt}

    categories_dict_by_name = {}

    for category in categories_json:
        category_id = category["id"]
        category_name = category["name"]
        category_parent_id = None
        if "parentId" in category:
            category_parent_id = category["parentId"]
        category_full_name = get_full_category_name(category_parent_id, category_name, child_category_dict)

        categories_dict_by_name[category_full_name] = category_id
    
    return categories_dict_by_name

def read_file_to_add_segments(file_path):
    read_df = None
    try:
        # Skip row 2 ([1]) tha indicates if field is mandatory or not
        read_df = pd.read_excel(file_path, sheet_name="Adform", skiprows=[1])
    except:
        return {"message":"File Path '{}' is not found".format(file_path)}

    access_token = authenticate()
    categories_json = get_categories(access_token)
    categories_dict_by_name = store_category_in_dict_by_name(categories_json)

    ref_id_list = read_df["Ref ID"]
    segment_name_list = read_df["Segment Name"]
    region_list = read_df["Region"]
    fee_list = read_df["Fee"]
    ttl_list = read_df["TTL"]
    segment_id_list = []
    write_category_result_list = []
    write_add_segment_result_list = []

    row_counter = 0
    for segment_name in segment_name_list:
        region = region_list[row_counter]
        index_of_separator = segment_name.rfind(" - ")

        category_success = True

        # Unable to find separator
        if index_of_separator == -1:
            segment_id_list.append(None)
            write_category_result_list.append("No separator ' - ' is found in the Segment Name")
            write_add_segment_result_list.append(None)
            category_success = False
        else:
            child_segment_name = segment_name[index_of_separator + 3:]
            category_name = segment_name[0:index_of_separator]

            if category_name in categories_dict_by_name:
                category_id = categories_dict_by_name[category_name]
            else:
                parent_category_id = None
                category_name_list = category_name.split(" - ")

                # if category does not exist, split the category name and check each and add if not available
                is_parentmost = True
                category_name_to_check = ""
                temp_parent_category_id = None
                for category_part_name in category_name_list:
                    if is_parentmost:
                        category_name_to_check = category_part_name
                    else:
                        category_name_to_check = category_name_to_check + " - " + category_part_name

                    print("Category Name to Check: {}".format(category_name_to_check))

                    if category_name_to_check in categories_dict_by_name:
                        temp_parent_category_id = categories_dict_by_name[category_name_to_check]
                    else:
                        temp_parent_category_id = add_category(access_token, category_part_name, region, temp_parent_category_id)

                        if temp_parent_category_id == None:
                            segment_id_list.append(None)
                            write_category_result_list.append("Error creating category: {}".format(category_part_name))
                            write_add_segment_result_list.append(None)
                            category_success = False
                        # category creation success
                        else:
                            categories_dict_by_name[category_name_to_check] = temp_parent_category_id

                    is_parentmost = False

                # if childmost category creation is successful
                if category_success:
                    category_id = temp_parent_category_id

            # category has been created/found, to create segment
            if category_success:
                write_category_result_list.append("OK")

                ref_id = ref_id_list[row_counter]
                fee = fee_list[row_counter]
                ttl = ttl_list[row_counter]

                fee_and_ttl_is_numeric = True
                try:
                    fee = int(fee)
                    ttl = int(ttl)
                except:
                    fee_and_ttl_is_numeric = False
                    segment_id_list.append(None)
                    write_add_segment_result_list.append("TTL and Fee have to be numeric")

                if fee_and_ttl_is_numeric:
                    status_code, output = add_segment(access_token, region, category_id, ref_id, fee, ttl, child_segment_name)
                    if status_code == 201:
                        segment_id_list.append(output)
                        write_add_segment_result_list.append("OK")
                    else:
                        segment_id_list.append(None)
                        write_add_segment_result_list.append(output)

        row_counter += 1

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    # print("Ref ID Length: {}".format(len(ref_id_list)))
    # print("Segment Name Length: {}".format(len(segment_name_list)))
    # print("Region Length: {}".format(len(region_list)))
    # print("Fee Length: {}".format(len(fee_list)))
    # print("TTL Length: {}".format(len(ttl_list)))
    # print("Segment ID Length: {}".format(len(segment_id_list)))
    # print("Category Result Length: {}".format(len(write_category_result_list)))
    # print("Add Segment Result Length: {}".format(len(write_add_segment_result_list)))

    write_df = pd.DataFrame({
                        "RefID":ref_id_list,
                        "Segment Name":segment_name_list,
                        "Region":region_list,
                        "Fee":fee_list,
                        "TTL":ttl_list,
                        "Segment ID":segment_id_list,
                        "Category Result":write_category_result_list,
                        "Add Segment Result":write_add_segment_result_list
                })
    return write_excel.write(write_df, file_name + "_output_add_segments")