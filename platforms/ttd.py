import requests
import write_excel
import variables
import pandas as pd

# API URL address
URL_AUTHENTICATION = "https://api.thetradedesk.com/v3/authentication"
URL_CREATE = "https://api.thetradedesk.com/v3/thirdpartydata"
URL_EDIT = "https://api.thetradedesk.com/v3/thirdpartydata"
URL_QUERY = "https://api.thetradedesk.com/v3/thirdpartydata/query"

# Folder to retrieve uploaded file
UPLOAD_FOLDER = variables.UPLOAD_FOLDER

# Login credentials
LOGIN = "dataops@eyeota.com"
PASSWORD = "Dat@ops1"

# Provider ID
PROVIDER_ID = "eyeota"


# callAPI function will decide what function in ttd to call. platform_manager.py will call this function 
# if platform selected is "The Trade Desk"
def callAPI(function, file_path):
    output = "ERROR: option is not available"
    if (function == "Query"):
        output = getQueryAll()
    else:
        output = read_file(file_path, function)
    return output

# get authentication code. return None if credentials fail
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

    # auth_code is null if credentials are incorrect
    try:
        auth_code = auth_data["Token"]
        return auth_code
    except:
        return auth_code

# query all the third party data in Trade Desk system
def getQueryAll():
    auth_code = getAuthenticationCode()
    if (auth_code == None):
        return{'message':"ERROR: getting TTD Auth Code. Please check <b>ttd.py</b> if credentials are correct."}

    query_data = requests.post(URL_QUERY,
                    headers={
                        'Content-Type':'application/json',
                        'TTD-Auth': auth_code
                    },
                    json={
                        'ProviderId':"eyeota",
                        'PageStartIndex':0,
                        'PageSize':None
                    }).json()
    # write to file
    return processJsonOutput(query_data, "query")

def read_file(file_path, function):
    read_df = pd.read_excel(file_path, sheet_name=0)

    segment_id_list = read_df['Segment ID']
    parent_segment_id_list = read_df['Parent Segment ID']
    segment_name_list = read_df['Segment Name']
    segment_description_list = read_df['Segment Description']
    buyable_list = read_df['Buyable']

    output = None
    result_list = []
    try:
        for row_num in segment_id_list.index:
            if row_num < 1:
                continue
            
            provider_element_id = segment_id_list[row_num]
            parent_element_id = parent_segment_id_list[row_num]
            display_name = segment_name_list[row_num]
            buyable = buyable_list[row_num]
            if (buyable.lower == "buyable"):
                buyable = True
            else:
                buyable = False
            description = segment_description_list[row_num]
            
            # to do - call for add or edit function based on the function
            output = add_or_edit(provider_element_id, parent_element_id, display_name, buyable, description, function)
            result_list.append(output)
    except Exception as e:
        print("ERROR: " + e)
    finally: 
        json_output = {'Result':result_list}
        return processJsonOutput(json_output, function)

# Add function returns a json format for each call, to be appended to the results before processJsonOutput
def add_or_edit(provider_element_id, parent_element_id, display_name, buyable, description, function):
    auth_code = getAuthenticationCode()
    if (auth_code == None):
        return{'message':"ERROR: getting TTD Auth Code. Please check <b>ttd.py</b> if credentials are correct."}

    if (function == "Add"):
        output_data = requests.post(URL_CREATE,
                        headers={
                            'Content-Type':'application/json',
                            'TTD-Auth': auth_code
                        },
                        json={
                            'ProviderId':PROVIDER_ID,
                            'ProviderElementId':provider_element_id,
                            'ParentElementId':parent_element_id,
                            'DisplayName':display_name,
                            'Buyable':buyable,
                            'Description':description
                        }).json()
        return output_data
    elif (function == "Edit"):
        url_to_call = URL_EDIT
    else:
        return{'message':'ERROR: no such function ' + function}
        
# based on the output from TTD API, format them into json format to write to file
def processJsonOutput(json_output, function):
    write_provider_id = []
    write_provider_element_id = []
    write_parent_element_id = []
    write_display_name = []
    write_buyable = []
    write_description = []
    write_audience_size = []

    for row in json_output['Result']:
        provider_id = row['ProviderId']
        provider_element_id = row['ProviderElementId']
        parent_element_id = row['ParentElementId']
        display_name = row['DisplayName']
        buyable = row['Buyable']
        description = row['Description']
        audience_size = row['AudienceSize']

        if not provider_id is None:
            provider_id.encode('utf-8').strip()

        if not provider_element_id is None:
            provider_element_id = provider_element_id.encode('utf-8').strip()
        
        if not parent_element_id is None:
            parent_element_id = parent_element_id.encode('utf-8').strip()

        if not display_name is None:
            display_name = display_name.encode('utf-8').strip()

        if not buyable is None and not isinstance(buyable, bool):
            buyable = buyable.encode('utf-8').strip()
        
        if not description is None:
            description = description.encode('utf-8').strip()

        if not audience_size is None and not isinstance(audience_size, int):
            audience_size = audience_size.encode('utf-8').strip()

        write_provider_id.append(provider_id)
        write_provider_element_id.append(provider_element_id)
        write_parent_element_id.append(parent_element_id)
        write_display_name.append(display_name)
        write_buyable.append(buyable)
        write_description.append(description)
        write_audience_size.append(audience_size)

    write_df = pd.DataFrame({
                                "Provider ID":write_provider_id,
                                "Segment ID":write_provider_element_id,
                                "Parent Segment ID":write_parent_element_id,
                                "Segment Name":write_display_name,
                                "Buyable":write_buyable,
                                "Description":write_description,
                                "Audience Size":write_audience_size
                            })
    return write_excel.write(write_df, "The_Trade_Desk_" + function)