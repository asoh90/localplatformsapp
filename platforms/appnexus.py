import requests
import write_excel
import variables
import pandas as pd
import os

MEMBER_ID = 1706

# API URL
URL_HOME = 'https://api.appnexus.com/'
# URL_HOME = 'https://api-test.appnexus.com/'
URL_AUTH = URL_HOME + "auth"
URL_SEGMENT = URL_HOME + "segment"
URL_BUYER_MEMBER_DATA_SHARING = URL_HOME + "member-data-sharing"
URL_SEGMENT_BILLING_CATEGORY = URL_HOME + "segment-billing-category"

# Folder to retrieve uploaded file
UPLOAD_FOLDER = variables.UPLOAD_FOLDER

# Login credentials
login = None
password = None

auth_token = None
RETRIEVE_SEGMENTS_NUM_ELEMENTS = 100

def callAPI(function, file_path):
    try:
        # Login credentials
        global login; login = variables.login_credentials['AppNexus']['Login']
        global password; password = variables.login_credentials['AppNexus']['PW']
    except:
        return {"message":"ERROR: Incorrect login credentials! Please download 'asoh-flask-deploy.sh' file from <a href='https://eyeota.atlassian.net/wiki/pages/viewpageattachments.action?pageId=127336529&metadataLink=true'>Confluence</a> again!>"}


    output = {"message":"ERROR: option is not available"}
    authenticate()
    if (function == "Query Segments"):
        output = query_all_segments()
    elif (function == "Add Segments"):
        output = read_file_to_add_segments(file_path)
    elif (function == "Edit Segments"):
        output = read_file_to_edit_segments(file_path)
    elif (function == "Add Segment Billings"):
        output = read_file_to_add_segment_billings(file_path)
    elif (function == "Edit Segment Billings"):
        output = read_file_to_edit_segment_billings(file_path)
    elif (function == "Add Existing Segments to Specific Buyer Member"):
        output = read_file_to_add_existing_segments_to_buyer_member(file_path)
    elif (function == "Retrieve Segment IDs"):
        output = read_file_to_retrieve_segment_id(file_path)
    elif (function == "Retrieve Buyer Member Segments"):
        output = read_file_to_retrieve_buyer_member_segments(file_path)
    return output

def authenticate():
    auth_credentials = {'username':login,'password':password}
    auth_json = requests.post(URL_AUTH,
                              headers={
                                  'Content-Type':'application/json'
                              },
                              json={
                                  'auth':auth_credentials
                              }).json()
    response = auth_json['response']
    global auth_token; auth_token = response['token']

# Start Query Segments functions
def query_all_segments():
    total_segments = 1
    start_element = 0

    write_segment_id_list = []
    write_code_list = []
    write_segment_name_list = []
    write_price_list = []
    write_duration_list = []
    write_member_id_list = []
    write_state_list = []
    write_last_modified_list = []

    while start_element < total_segments:
        retrieve_response = retrieve_segments(start_element, RETRIEVE_SEGMENTS_NUM_ELEMENTS)
        if ("message" in retrieve_response):
            return retrieve_response

        if (total_segments == 1):
            total_segments = retrieve_response["count"]
        print("Retrieving {} of {} segments".format(start_element, total_segments))
        
        start_element += RETRIEVE_SEGMENTS_NUM_ELEMENTS
        response_segment = retrieve_response["segments"]

        for segment in response_segment:
            write_segment_id_list.append(segment["id"])
            write_code_list.append(segment["code"])
            write_segment_name_list.append(segment["short_name"])
            write_price_list.append(segment["price"])
            write_duration_list.append(segment["expire_minutes"])
            write_member_id_list.append(segment["member_id"])
            write_state_list.append(segment["state"])
            write_last_modified_list.append(segment["last_modified"])

    write_df = pd.DataFrame({
                    "Segment id":write_segment_id_list,
                    'code':write_code_list,
                    'Segment Name':write_segment_name_list,
                    'Price':write_price_list,
                    'Duration':write_duration_list,
                    'Member ID':write_member_id_list,
                    'State':write_state_list,
                    'Last Modified':write_last_modified_list,
                })
    return write_excel.write(write_df, "AppNexus_Retrieve")

def retrieve_segments(start_element, num_elements):
    try:
        request_to_send = requests.get(URL_SEGMENT,
                                    headers={
                                        'Content-Type':'application/json',
                                        'Authorization':auth_token
                                    },
                                    params={
                                        "start_element":start_element,
                                        "num_elements":num_elements,
                                        "member_id":MEMBER_ID
                                    })
        print("Retrieve Request: " + request_to_send.url)
        retrieve_response = request_to_send.json()
        return retrieve_response["response"]
    except:
        return {"messsage":"Unable to retrieve all segments where start_element: {}  |  num_elements: {}".format(start_element, num_elements)}
# End Query Segments functions

# Start Add Segments functions
def read_file_to_add_segments(file_path):
    read_df = None
    try:
        # Skip row 2 ([1]) tha indicates if field is mandatory or not
        read_df = pd.read_excel(file_path, sheet_name="AppNexus", skiprows=[1])
    except:
        return {"message":"File Path '{}' is not found".format(file_path)}
    
    code_list = read_df["code"]
    segment_name_list = read_df["Segment Name"]
    price_list = read_df["Price"]
    duration_list = read_df["Duration"]
    state_list = read_df["State"]
    is_public_list = read_df["Is Public"]
    data_category_list = read_df["Data Category ID"]
    buyer_member_id_list = read_df["Buyer Member ID"]

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    write_segment_id_list = []
    write_code_list = []
    write_segment_name_list = []
    write_price_list = []
    write_duration_list = []
    write_member_id_list = []
    write_state_list = []
    write_is_public_list = []
    write_data_category_list = []
    write_buyer_member_id_list = []
    write_response = []
    write_billing_response = []

    private_segment_list = {}

    for i in range(len(code_list)):
        current_code = code_list[i]
        current_segment_name = segment_name_list[i]
        current_price = price_list[i]
        current_duration = duration_list[i]
        current_state = state_list[i]
        current_is_public = is_public_list[i]
        current_data_category_id = data_category_list[i]
        current_buyer_member_id = buyer_member_id_list[i]

        add_response = add_segment(current_code, current_segment_name, current_price, current_duration, current_state)
        current_segment_id = add_response["id"]
        # Private segments will append to a list to be added to specific buyer member
        if not current_is_public and not current_segment_id == None:
            # Buyer member does not already have a list
            if not current_buyer_member_id in private_segment_list:
                private_segment_list[current_buyer_member_id] = {}

            buyer_member_private_segment = private_segment_list[current_buyer_member_id]
            buyer_member_private_segment[current_segment_id] = {
                                                        "segment_id":current_segment_id,
                                                        "code":current_code,
                                                        "segment_name":current_segment_name,
                                                        "price":current_price,
                                                        "duration":current_duration,
                                                        "state":current_state,
                                                        "is_public":current_is_public,
                                                        "data_category_id":current_data_category_id,
                                                        "response":None
                                                    }
        # Public segments can add response to the list
        else:
            write_segment_id_list.append(current_segment_id)
            write_code_list.append(current_code)
            write_segment_name_list.append(current_segment_name)
            write_price_list.append(current_price)
            write_duration_list.append(current_duration)
            write_member_id_list.append(MEMBER_ID)
            write_state_list.append(current_state)
            write_is_public_list.append(current_is_public)
            write_data_category_list.append(current_data_category_id)
            write_buyer_member_id_list.append(current_buyer_member_id)
            write_response.append(add_response["response"])
            if current_segment_id == None:
                write_billing_response.append("")
            else:
                add_billing_response = add_segment_billing(current_segment_id, current_state, current_data_category_id, current_is_public)
                write_billing_response.append(add_billing_response)

    # Add private segments to specific buyer_member_id
    private_segments_to_add = private_segment_list.keys()
    if len(private_segments_to_add) > 0:
        for buyer_member_id in private_segments_to_add:
            buyer_member_private_segment_list = private_segment_list[buyer_member_id]
            private_segment_response = refresh_segments(buyer_member_id, buyer_member_private_segment_list)

            for segment_id in private_segment_response:
                private_segment_details = private_segment_response[segment_id]
                write_segment_id_list.append(private_segment_details["segment_id"])
                write_code_list.append(private_segment_details["code"])
                write_segment_name_list.append(private_segment_details["segment_name"])
                write_price_list.append(private_segment_details["price"])
                write_duration_list.append(private_segment_details["duration"])
                write_member_id_list.append(MEMBER_ID)
                write_state_list.append(private_segment_details["state"])
                write_is_public_list.append(private_segment_details["is_public"])
                write_data_category_list.append(private_segment_details["data_category_id"])
                write_buyer_member_id_list.append(buyer_member_id)
                write_response.append(private_segment_details["response"])

    # Print result of creating segments
    write_df = pd.DataFrame({
                    "Segment ID":write_segment_id_list,
                    'code':write_code_list,
                    'Segment Name':write_segment_name_list,
                    'Price':write_price_list,
                    'Duration':write_duration_list,
                    'Member ID':write_member_id_list,
                    'State':write_state_list,
                    'Is Public':write_is_public_list,
                    'Data Category ID':write_data_category_list,
                    'Buyer Member ID':write_buyer_member_id_list,
                    'Add Segment Response':write_response,
                    'Add Billing Response':write_billing_response
                })
    return write_excel.write(write_df, file_name + "_output_add_segments")

def read_file_to_edit_segments(file_path):
    read_df = None
    try:
        # Skip row 2 ([1]) tha indicates if field is mandatory or not
        read_df = pd.read_excel(file_path, sheet_name="AppNexus", skiprows=[1])
    except:
        return {"message":"File Path '{}' is not found".format(file_path)}
    
    segment_id_list = read_df["Segment ID"]
    code_list = read_df["code"]
    segment_name_list = read_df["Segment Name"]
    price_list = read_df["Price"]
    duration_list = read_df["Duration"]
    state_list = read_df["State"]
    is_public_list = read_df["Is Public"]
    data_category_list = read_df["Data Category ID"]
    buyer_member_id_list = read_df["Buyer Member ID"]

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    write_segment_id_list = []
    write_code_list = []
    write_segment_name_list = []
    write_price_list = []
    write_duration_list = []
    write_member_id_list = []
    write_state_list = []
    write_is_public_list = []
    write_data_category_list = []
    write_buyer_member_id_list = []
    write_response = []


    for i in range(len(code_list)):
        current_code = code_list[i]
        current_segment_name = segment_name_list[i]
        current_price = price_list[i]
        current_duration = duration_list[i]
        current_state = state_list[i]

        edit_response = edit_segment(current_code, current_segment_name, current_price, current_duration, current_state)

        segment_id_added = False
        code_added = False
        segment_name_added = False
        price_added = False
        duration_added = False
        state_added = False
        response_added = False
        try:
            edited_segment = edit_response["segment"]

            write_segment_id_list.append(edited_segment["id"])
            segment_id_added = True
            write_code_list.append(edited_segment["code"])
            code_added = True
            write_segment_name_list.append(edited_segment["short_name"])
            segment_name_added = True
            write_price_list.append(edited_segment["price"])
            price_added = True
            write_duration_list.append(edited_segment["expire_minutes"])
            duration_added = True
            write_state_list.append(edited_segment["state"])
            state_added = True
            write_response.append(edit_response["status"])
            response_added = True
        except:
            if not segment_id_added:
                write_segment_id_list.append(segment_id_list[i])
            if not code_added:
                write_code_list.append(current_code)
            if not segment_name_added:
                write_segment_name_list.append(current_segment_name)
            if not price_added:
                write_price_list.append(current_price)
            if not duration_added:
                write_duration_list.append(current_duration)
            if not state_added:
                write_state_list.append(current_state)
            if not response_added:
                error_message = edit_response
                write_response.append(error_message)

        write_member_id_list.append(MEMBER_ID)
        write_is_public_list.append(is_public_list[i])
        write_data_category_list.append(data_category_list[i])
        write_buyer_member_id_list.append(buyer_member_id_list[i])

    write_df = pd.DataFrame({
                "Segment ID":write_segment_id_list,
                'code':write_code_list,
                'Segment Name':write_segment_name_list,
                'Price':write_price_list,
                'Duration':write_duration_list,
                'Member ID':write_member_id_list,
                'State':write_state_list,
                'Is Public':write_is_public_list,
                'Data Category ID':write_data_category_list,
                'Buyer Member ID':write_buyer_member_id_list,
                'Response':write_response
            })
        
    return write_excel.write(write_df, file_name + "_output_edit_segments")

def add_segment(code, segment_name, price, duration, state):
    segment_to_add = {
                        "code":str(code),
                        "expire_minutes":int(duration),
                        "short_name":segment_name,
                        "price":float(price),
                        "state":state
                    }
    try:
        request_to_send = requests.post(URL_SEGMENT,
                                    headers={
                                        'Content-Type':'application/json',
                                        'Authorization':auth_token
                                    },
                                    params={
                                        'member_id':MEMBER_ID
                                    },
                                    json={
                                        'segment':segment_to_add
                                    })
        print("Add Request: " + request_to_send.url)
        add_response = request_to_send.json()
        # print(add_response)
        response = add_response["response"]
        return {'id':response["id"],"response":response["status"]}
    except:
        return {'id':None,"response":response["error"]}

def edit_segment(code, segment_name, price, duration, state):
    segment_to_edit = {
                        "member_id":MEMBER_ID,
                        "code":str(code),
                        "expire_minutes":int(duration),
                        "short_name":segment_name,
                        "price":float(price),
                        "state":state
                    }
    try:
        request_to_send = requests.put(URL_SEGMENT,
                                    headers={
                                        'Content-Type':'application/json',
                                        'Authorization':auth_token
                                    },
                                    params={
                                        'member_id':MEMBER_ID,
                                        'code':code
                                    },
                                    json={
                                        'segment':segment_to_edit
                                    })
        print("Edit Request: " + request_to_send.url)
        edit_response = request_to_send.json()
        # print(add_response)
        response = edit_response["response"]
        return response
    except:
        return response["error"]

def refresh_segments(buyer_member_id, buyer_member_private_segment_list):
    retrieve_results = retrieve_segments_for_member(buyer_member_id)
    record_id = retrieve_results["record_id"]
    current_segment_list = retrieve_results["segment_list"]
    if current_segment_list == None:
        return
    current_segment_id_list = []
    updated_segment_list = []
    
    for current_segment in current_segment_list:
        current_segment_id_list.append(current_segment["id"])
        updated_segment_list.append({"id":current_segment["id"]})

    for private_segment in buyer_member_private_segment_list:
        if private_segment not in current_segment_id_list:
            updated_segment_list.append({"id":buyer_member_private_segment_list[private_segment]["segment_id"]})
            current_segment_id_list.append(buyer_member_private_segment_list[private_segment]["segment_id"])

    response = refresh_segment_ids(record_id, updated_segment_list)

    for private_segment in buyer_member_private_segment_list:
        buyer_member_private_segment_list[private_segment]["response"] = response

    return buyer_member_private_segment_list

def retrieve_segments_for_member(buyer_member_id):
    try:
        request_to_send = requests.get(URL_BUYER_MEMBER_DATA_SHARING,
                                            headers={
                                                'Content-Type':'application/json',
                                                'Authorization':auth_token
                                            },
                                            params={
                                                'data_member_id':MEMBER_ID,
                                                'buyer_member_id':buyer_member_id
                                            }
                                        )
        print("Retrieve Request URL: " + request_to_send.url)
        retrieve_response = request_to_send.json()
        member_data_sharings = retrieve_response["response"]["member_data_sharings"][0]
        segment_list = member_data_sharings["segments"]
        record_id = member_data_sharings["id"]
        print("Record ID: {}".format(record_id))
        return {"record_id":record_id,"segment_list":segment_list}
    except Exception:
        print(retrieve_response["response"]["error"])

def refresh_segment_ids(record_id, new_segment_id_list):
    print("Refreshing record id: {}".format(record_id))
    segment_list_to_send = {"segments":new_segment_id_list}

    # try:
    request_to_send = requests.put(URL_BUYER_MEMBER_DATA_SHARING,
                                            headers={
                                                'Content-Type':'application/json',
                                                'Authorization':auth_token
                                            },
                                            params={
                                                'id':record_id
                                            },
                                            json={
                                                'member_data_sharing':segment_list_to_send
                                            })
    print("Refresh Request URL: " + request_to_send.url)
    refresh_response = request_to_send.json()
    return refresh_response["response"]["status"]
    # except Exception as e:
    #     return refresh_response["response"]["error"]
# End Add Segments functions

def read_file_to_retrieve_segment_id(file_path):
    read_df = None
    try:
        # Skip row 2 ([1]) tha indicates if field is mandatory or not
        read_df = pd.read_excel(file_path, sheet_name="AppNexus", skiprows=[1])
    except:
        return {"message":"File Path '{}' is not found".format(file_name)}
    
    code_list = read_df["code"]
    is_public_list = read_df["Is Public"]
    data_category_list = read_df["Data Category ID"]
    buyer_member_id_list = read_df["Buyer Member ID"]

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    write_segment_id_list = []
    write_segment_name_list = []
    write_price_list = []
    write_duration_list = []
    write_member_id_list = []
    write_state_list = []
    write_is_public_list = []
    write_data_category_list = []
    write_buyer_member_id_list = []

    for row_num in range(len(code_list)):
        current_code = code_list[row_num]

        retrieved_segment_details = retrieve_segment_id(current_code)
        write_segment_id_list.append(retrieved_segment_details["id"])
        write_segment_name_list.append(retrieved_segment_details["short_name"])
        write_price_list.append(retrieved_segment_details["price"])
        write_duration_list.append(retrieved_segment_details["expire_minutes"])
        write_member_id_list.append(MEMBER_ID)
        write_state_list.append(retrieved_segment_details["state"])

    write_df = pd.DataFrame({
                    "Segment ID":write_segment_id_list,
                    'code':code_list,
                    'Segment Name':write_segment_name_list,
                    'Price':write_price_list,
                    'Duration':write_duration_list,
                    'Member ID':write_member_id_list,
                    'State':write_state_list,
                    'Is Public':is_public_list,
                    'Data Category ID':data_category_list,
                    'Buyer Member ID':buyer_member_id_list
                })
    return write_excel.write(write_df, file_name + "_output_retrieve_segment_ids")

def retrieve_segment_id(code):
    try:
        request_to_send = requests.get(URL_SEGMENT,
                                            headers={
                                                'Content-Type':'application/json',
                                                'Authorization':auth_token
                                            },
                                            params={
                                                'code':code
                                            }
                                        )
        print("Retrieve Segment ID Request URL: " + request_to_send.url)
        retrieve_response = request_to_send.json()
        segment = retrieve_response["response"]["segment"]
        return segment
    except Exception:
        return "Unable to find code {}".format(code)

def read_file_to_add_existing_segments_to_buyer_member(file_path):
    read_df = None
    try:
        # Skip row 2 ([1]) tha indicates if field is mandatory or not
        read_df = pd.read_excel(file_path, sheet_name="AppNexus", skiprows=[1])
    except:
        return {"message":"File Path '{}' is not found".format(file_name)}
    
    segment_id_list = read_df["Segment ID"]
    code_list = read_df["code"]
    segment_name_list = read_df["Segment Name"]
    price_list = read_df["Price"]
    duration_list = read_df["Duration"]
    state_list = read_df["State"]
    is_public_list = read_df["Is Public"]
    data_category_list = read_df["Data Category ID"]
    buyer_member_id_list = read_df["Buyer Member ID"]

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    write_segment_id_list = []
    write_code_list = []
    write_segment_name_list = []
    write_price_list = []
    write_duration_list = []
    write_member_id_list = []
    write_state_list = []
    write_is_public_list = []
    write_data_category_list = []
    write_buyer_member_id_list = []
    write_response = []

    private_segment_dict = {}

    for row_num in range(len(segment_id_list)):
        current_segment_id = int(segment_id_list[row_num])
        current_code = code_list[row_num]
        current_segment_name = segment_name_list[row_num]
        current_price = price_list[row_num]
        current_duration = duration_list[row_num]
        current_state = state_list[row_num]
        current_is_public = is_public_list[row_num]
        current_data_category_id = data_category_list[row_num]
        current_buyer_member_id = buyer_member_id_list[row_num]

        if not current_buyer_member_id in private_segment_dict:
            private_segment_dict[current_buyer_member_id] = {}

        buyer_member_private_segment = private_segment_dict[current_buyer_member_id]

        buyer_member_private_segment[current_segment_id] = {
                                                    "segment_id":current_segment_id,
                                                    "code":current_code,
                                                    "segment_name":current_segment_name,
                                                    "price":current_price,
                                                    "duration":current_duration,
                                                    "state":current_state,
                                                    "is_public":current_is_public,
                                                    "data_category_id":current_data_category_id,
                                                    "response":None
                                                }

    private_segments_to_add = private_segment_dict.keys()
    if len(private_segments_to_add) > 0:
        for buyer_member_id in private_segments_to_add:
            buyer_member_private_segment_list = private_segment_dict[buyer_member_id]
            private_segment_response = refresh_segments(buyer_member_id, buyer_member_private_segment_list)

            for segment_id in private_segment_response:
                private_segment_details = private_segment_response[segment_id]
                write_segment_id_list.append(private_segment_details["segment_id"])
                write_code_list.append(private_segment_details["code"])
                write_segment_name_list.append(private_segment_details["segment_name"])
                write_price_list.append(private_segment_details["price"])
                write_duration_list.append(private_segment_details["duration"])
                write_member_id_list.append(MEMBER_ID)
                write_state_list.append(private_segment_details["state"])
                write_is_public_list.append(private_segment_details["is_public"])
                write_data_category_list.append(private_segment_details["data_category_id"])
                write_buyer_member_id_list.append(buyer_member_id)
                write_response.append(private_segment_details["response"])

    # Print result of creating segments
    write_df = pd.DataFrame({
                    "Segment ID":write_segment_id_list,
                    'code':write_code_list,
                    'Segment Name':write_segment_name_list,
                    'Price':write_price_list,
                    'Duration':write_duration_list,
                    'Member ID':write_member_id_list,
                    'State':write_state_list,
                    'Is Public':write_is_public_list,
                    'Data Category ID':write_data_category_list,
                    'Buyer Member ID':write_buyer_member_id_list,
                    'Response':write_response
                })
    return write_excel.write(write_df, file_name + "_output_add_to_buyer")

def read_file_to_retrieve_buyer_member_segments(file_path):
    read_df = None
    try:
        # Skip row 2 ([1]) tha indicates if field is mandatory or not
        read_df = pd.read_excel(file_path, sheet_name="AppNexus", skiprows=[1])
    except:
        return {"message":"File Path '{}' is not found".format(file_path)}

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]
    
    buyer_member_id_list = read_df["Buyer Member ID"]

    write_segment_id_list = []
    write_segment_name_list = []
    write_buyer_member_id_list = []

    unique_buyer_id_list = []
    for buyer_id in buyer_member_id_list:
        if not buyer_id in unique_buyer_id_list:
            unique_buyer_id_list.append(buyer_id)

    for buyer_member_id in unique_buyer_id_list:
        member_segments_response = retrieve_segments_for_member(buyer_member_id)
        buyer_member_segments = member_segments_response["segment_list"]

        for buyer_member_segment in buyer_member_segments:
            write_segment_id_list.append(buyer_member_segment["id"])
            write_segment_name_list.append(buyer_member_segment["name"])
            write_buyer_member_id_list.append(buyer_member_id)
    
    # Print result of creating segments
    write_df = pd.DataFrame({
                    "Segment ID":write_segment_id_list,
                    'Segment Name':write_segment_name_list,
                    'Buyer Member ID':write_buyer_member_id_list
                })
    return write_excel.write(write_df, file_name + "_output_buyer_segments")

# Start of Segment Billing Functions
def read_file_to_add_segment_billings(file_path):
    read_df = None
    try:
        # Skip row 2 ([1]) tha indicates if field is mandatory or not
        read_df = pd.read_excel(file_path, sheet_name="AppNexus", skiprows=[1])
    except:
        return {"message":"File Path '{}' is not found".format(file_path)}
    
    segment_id_list = read_df["Segment ID"]
    code_list = read_df["code"]
    segment_name_list = read_df["Segment Name"]
    price_list = read_df["Price"]
    duration_list = read_df["Duration"]
    state_list = read_df["State"]
    is_public_list = read_df["Is Public"]
    data_category_list = read_df["Data Category ID"]
    buyer_member_id_list = read_df["Buyer Member ID"]
    write_response = []
    member_id_list = []

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    for i in range(len(segment_id_list)):
        current_segment_id = segment_id_list[i]
        current_state = state_list[i]
        current_data_category_id = data_category_list[i]
        current_is_public = is_public_list[i]

        add_segment_billing_response = add_segment_billing(current_segment_id, current_state, current_data_category_id, current_is_public)
        write_response.append(add_segment_billing_response)
        member_id_list.append(MEMBER_ID)
    
    write_df = pd.DataFrame({
                    "Segment ID":segment_id_list,
                    'code':code_list,
                    'Segment Name':segment_name_list,
                    'Price':price_list,
                    'Duration':duration_list,
                    'Member ID':member_id_list,
                    'State':state_list,
                    'Is Public':is_public_list,
                    'Data Category ID':data_category_list,
                    'Buyer Member ID':buyer_member_id_list,
                    'Response':write_response
                })
    return write_excel.write(write_df, file_name + "_output_add_billing.xlsx")

def read_file_to_edit_segment_billings(file_path):
    read_df = None
    try:
        # Skip row 2 ([1]) tha indicates if field is mandatory or not
        read_df = pd.read_excel(file_path, sheet_name="AppNexus", skiprows=[1])
    except:
        return {"message":"File Path '{}' is not found".format(file_path)}
    
    segment_id_list = read_df["Segment ID"]
    code_list = read_df["code"]
    segment_name_list = read_df["Segment Name"]
    price_list = read_df["Price"]
    duration_list = read_df["Duration"]
    state_list = read_df["State"]
    is_public_list = read_df["Is Public"]
    data_category_list = read_df["Data Category ID"]
    buyer_member_id_list = read_df["Buyer Member ID"]
    write_response = []

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    for i in range(len(segment_id_list)):
        current_segment_id = segment_id_list[i]
        current_state = state_list[i]
        current_data_category_id = data_category_list[i]
        current_is_public = is_public_list[i]

        edit_segment_billing = edit_segment_billing(current_segment_id, current_state, current_data_category_id, current_is_public)


def add_segment_billing(segment_id, state, data_category_id, is_public):
    segment_billing_to_add = {
                                "segment_id":str(segment_id),
                                "data_provider_id":MEMBER_ID,
                                "data_category_id":str(data_category_id),
                                "active":str(state),
                                "is_public":str(is_public),
                                "member_id":MEMBER_ID,
                                "data_segment_type_id":"Audience"
                            }
    print(segment_billing_to_add)
    try:
        request_to_send = requests.post(URL_SEGMENT_BILLING_CATEGORY,
                                    headers={
                                        'Content-Type':'application/json',
                                        'Authorization':auth_token
                                    },
                                    params={
                                        'member_id':MEMBER_ID
                                    },
                                    json={
                                        'segment-billing-category':segment_billing_to_add
                                    })
        print("Add Segment Billing Request: " + request_to_send.url)
        add_segment_billing_response = request_to_send.json()
        return add_segment_billing_response["response"]["status"]
    except Exception:
        return add_segment_billing_response["response"]["error"]

def edit_segment_billing(segment_id, state, data_category_id, is_public):
    id = get_segment_billing_id(segment_id)
    segment_billing_to_edit = {
                                "id":str(id),
                                "segment_id":str(segment_id),
                                "data_provider_id":MEMBER_ID,
                                "data_category_id":str(data_category_id),
                                "active":str(state),
                                "is_public":str(is_public),
                                "member_id":MEMBER_ID,
                                "data_segment_type_id":"Audience"
                            }
    try:
        request_to_send = requests.put(URL_SEGMENT_BILLING_CATEGORY,
                                    headers={
                                        'Content-Type':'application/json',
                                        'Authorization':auth_token
                                    },
                                    params={
                                        'member_id':MEMBER_ID
                                    },
                                    json={
                                        'segment-billing-category':segment_billing_to_edit
                                    })
        print("Edit Segment Billing Request: " + request_to_send.url)
        edit_segment_billing_response = request_to_send.json()
        return edit_segment_billing_response["response"]["status"]
    except Exception:
        return edit_segment_billing_response["response"]["error"]

def get_segment_billing_id(segment_id):
    try:
        request_to_send = requests.get(URL_SEGMENT_BILLING_CATEGORY,
                                    headers={
                                        'Content-Type':'application/json',
                                        'Authorization':auth_token
                                    },
                                    params={
                                        'member_id':MEMBER_ID,
                                        'segment_id':segment_id
                                    })
        print("Get Segment Billing Request: " + request_to_send.url)
        get_segment_billing_response = request_to_send.json()
        return get_segment_billing_response["response"]["segment-billing-categories"][0]["id"]
    except Exception:
        print("Segment ID: {} cannot be found!".format(segment_id))

# End of Segment Billing Functions