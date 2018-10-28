import requests
import variables
import write_excel
import pandas as pd
import os
import numpy

URL = "https://api.demdex.com:443/"
AUTH_URL = URL + "oauth/token"
API_URL = URL + "v1/"
DATA_SOURCE_URL = API_URL + "datasources/"
DATA_FEED_URL = API_URL + "data-feeds/{}/plans"
TRAITS_URL = API_URL + "traits/"

CONTENT_TYPE = "application/x-www-form-urlencoded"
AUTHORIZATION = "Basic ZXllb3RhLWJhYWFtOnJvZDZsOWluamRzZmwyN2E2cGUybjNsam50cmhndnRpM3A5NGN1YnUyMXVzdjZ2MXBicg=="
GRANT_TYPE = "password"

# constants to add data source
DATA_SOURCE_ID_TYPE = "COOKIE"
DATA_EXPORT_RESTRICTIONS = ['PII', 'ONSITE_PERSONALIZATION']
DATA_SOURCE_TYPE = "GENERAL"
INBOUNDS2S = True
OUTBOUNDS2S = False

# Login credentials
username = None
password = None

def callAPI(platform, function, file_path):
    try:
        global username; username = variables.login_credentials['AdobeAAM']['Login']
        global password; password = variables.login_credentials['AdobeAAM']['PW']
    except:
        return {"message":"ERROR: Incorrect login credentials! Please download 'asoh-flask-deploy.sh' file from <a href='https://eyeota.atlassian.net/wiki/pages/viewpageattachments.action?pageId=127336529&metadataLink=true'>Confluence</a> again!>"}

    output = {"message":"ERROR: option is not available"}

    if function == "Add Segments":
        output = read_all_to_add_segments(file_path)
    elif function == "Query All Segments":
        output = query_all_segments()
    return output
    

def authenticate():
    data = {
                'grant_type':GRANT_TYPE,
                'username':username,
                'password':password
            }
    auth_json = requests.post(AUTH_URL,
                            headers={
                                'Content-Type':CONTENT_TYPE,
                                'Authorization':AUTHORIZATION
                            },
                            data=data).json()
    return auth_json["access_token"]

def get_data_feed(access_token, data_source_id):
    if access_token == None:
        access_token = authenticate()

    # Only Activation should be CPM, the rest should be fixed
    data_feed_dict = {"SEGMENTS_AND_OVERLAP_PRICE":None,"MODELING_PRICE":None,"ACTIVATION_PRICE":None,
                    "SEGMENTS_AND_OVERLAP_UoM":None,"MODELING_UoM":None,"ACTIVATION_UoM":None}
    get_data_feed_request = requests.get(DATA_FEED_URL.format(data_source_id),
                        headers={
                            'Content-Type':"application/json",
                            'Authorization':"Bearer " + access_token
                        })
    print("Get Data Feed URL: {}".format(get_data_feed_request.url))
    
    # No data feed for this data source
    if get_data_feed_request.status_code == 404:
        return data_feed_dict

    data_feed_json = get_data_feed_request.json()
    for data_feed in data_feed_json:
        useCase = data_feed["useCase"]
        billingUnit = data_feed["billingUnit"]
        price = data_feed["price"]

        # planId = data_feed["planId"]
        # dataSourceId = data_feed["dataSourceId"]
        # description = data_feed["description"]
        # status = data_feed["status"]
        # billingCycle = data_feed["billingCycle"]
        # createTime = data_feed["createTime"]
        # updateTime = data_feed["updateTime"]
        # crUID = data_feed["crUID"]
        # upUID = data_feed["upUID"]

        # with open("data_feed_plans.txt", "a+") as txtFile:
        #     txtFile.write(str(data_source_id)+"|"+str(useCase)+"|"+str(billingUnit)+"|"+str(price)+"|"+str(planId)+"|"+str(description)+"|"+str(status)+"|"+str(billingCycle)+"|"+str(createTime)+"|"+str(updateTime)+"|"+str(crUID)+"|"+str(upUID)+"\n")

        if len(useCase) == 1 and useCase[0] == "SEGMENTS_AND_OVERLAP":
            data_feed_dict["SEGMENTS_AND_OVERLAP_PRICE"] = price
            data_feed_dict["SEGMENTS_AND_OVERLAP_UoM"] = billingUnit
        elif len(useCase) == 1 and useCase[0] == "MODELING":
            data_feed_dict["MODELING_PRICE"] = price
            data_feed_dict["MODELING_UoM"] = billingUnit
        else:
            data_feed_dict["ACTIVATION_PRICE"] = price
            data_feed_dict["ACTIVATION_UoM"] = billingUnit

    return data_feed_dict

def get_all_data_source():
    access_token = authenticate()

    get_data_source_request = requests.get(DATA_SOURCE_URL,
                            headers={
                                'Content-Type':"application/json",
                                'Authorization':"Bearer " + access_token
                            })
    print("Get Data Source URL: {}".format(get_data_source_request.url))

    data_source_json = get_data_source_request.json()
    return access_token, data_source_json

def get_data_source_id_dict():
    access_token, data_source_json = get_all_data_source()
    data_source_dict = {}

    # commented out all the unused parameters
    for data_source in data_source_json:
        # pid = data_source["pid"]
        name = data_source["name"]
        # description = data_source["description"]
        # status = data_source["status"]
        # integrationCode = data_source["integrationCode"]
        # dataExportRestrictions = data_source["dataExportRestrictions"]
        # updateTime = data_source["updateTime"]
        # crUID = data_source["crUID"]
        # upUID = data_source["upUID"]
        # data_source_type = data_source["type"]
        # inboundS2S = data_source["inboundS2S"]
        # outboundS2S = data_source["outboundS2S"]
        # useAudienceManagerVisitorID = data_source["useAudienceManagerVisitorID"]
        # allowDataSharing = data_source["allowDataSharing"]
        # masterDataSourceIdProvider = data_source["masterDataSourceIdProvider"]
        # idType = data_source["idType"]
        # allowDeviceGraphSharing = data_source["allowDeviceGraphSharing"]
        # supportsAuthenticatedProfile = data_source["supportsAuthenticatedProfile"]
        # deviceGraph = data_source["deviceGraph"]
        # authenticatedProfileName = data_source["authenticatedProfileName"]
        # deviceGraphName = data_source["deviceGraphName"]
        dataSourceId = data_source["dataSourceId"]
        # containerIds = data_source["containerIds"]
        # samplingEnabled = data_source["samplingEnabled"]

        # Get data feed for Data Source ID
        data_feed_dict = get_data_feed(access_token, dataSourceId)
        segments_and_overlap_price = data_feed_dict["SEGMENTS_AND_OVERLAP_PRICE"]
        segments_and_overlap_uom = data_feed_dict["SEGMENTS_AND_OVERLAP_UoM"]
        modeling_price = data_feed_dict["MODELING_PRICE"]
        modeling_uom = data_feed_dict["MODELING_UoM"]
        activation_price = data_feed_dict["ACTIVATION_PRICE"]
        activation_uom = data_feed_dict["ACTIVATION_UoM"]

        data_source_dict[dataSourceId] = {"name":name, "segments_and_overlap_price":segments_and_overlap_price,"segments_and_overlap_uom":segments_and_overlap_uom,
                                            "modeling_price":modeling_price,"modeling_uom":modeling_uom,
                                            "activation_price":activation_price,"activation_uom":activation_uom}
    return data_source_dict

# able to search the data source by name, returns Data Source ID
# Used for adding traits to existing data source
def get_data_source_name_dict():
    access_token, data_source_json = get_all_data_source()
    data_source_dict = {}

    # see get_data_source_id_dict for full list of fields available
    for data_source in data_source_json:
        # pid = data_source["pid"]
        name = data_source["name"]
        # so that when searching for the data source id, ignores case sensitivity
        lowercase_name = name.lower()
        dataSourceId = data_source["dataSourceId"]

        data_source_dict[lowercase_name] = dataSourceId
    return data_source_dict

def get_traits(access_token):
    if access_token == None:
        access_token = authenticate()

    get_traits_request = requests.get(TRAITS_URL,
                            headers={
                                'Content-Type':"application/json",
                                'Authorization':"Bearer " + access_token
                            })
    print("Get Traits URL: {}".format(get_traits_request.url))

    traits_json = get_traits_request.json()
    return traits_json

# Adding Data Source will add the name as the description as well
def add_data_source(access_token, data_source_name):
    if access_token == None:
        access_token = authenticate()

    add_data_source_request = requests.post(DATA_SOURCE_URL,
                        headers={
                            'Content-Type':"application/json",
                            'Authorization':"Bearer " + access_token
                        },
                        params={
                            "idType":DATA_SOURCE_ID_TYPE,
                            "outboundS2S":OUTBOUNDS2S,
                            "name":data_source_name,
                            "description":data_source_name,
                            "inboundS2S":INBOUNDS2S,
                            "type":DATA_SOURCE_TYPE,
                            "dataExportRestrictions":DATA_EXPORT_RESTRICTIONS
                        })
    print("Add Data Source URL: {}".format(get_data_source_request.url))

    add_data_source_status = add_data_source_request.status_code
    add_data_source_json = add_data_source_request.json()
    data_source_id = add_data_source_json["dataSourceId"]

    return add_data_source_status, data_source_id

# Process of getting all segments:
# 1. get all the data sources
# 2. for each data source ID, get the data feeds (contains the price of segments_and_overlap, modeling, and activation)
# 3. get all the traits (these are your segments)
# 4. match them all together, you will get the segments to the data source, then to the data feeds to get the rates of each traits(segments)
def query_all_segments():
    segment_id_list = []
    segment_name_list = []
    segment_description_list = []
    segment_status_list = []
    data_source_id_list = []
    data_source_name_list = []
    segments_and_overlap_price_list = []
    segments_and_overlap_uom_list = []
    modeling_price_list = []
    modeling_uom_list = []
    activation_price_list = []
    activation_uom_list = []

    data_source_dict = get_data_source_id_dict()
    traits_json = get_traits(None)

    for trait in traits_json:
        # createTime = trait["createTime"]
        # updateTime = trait["updateTime"]
        sid = trait["sid"]
        # traitType = trait["traitType"]
        name = trait["name"]
        description = trait["description"]
        status = trait["status"]
        # pid = trait["pid"]
        # crUID = trait["crUID"]
        # upUID = trait["upUID"]
        # integrationCode = trait["integrationCode"]
        dataSourceId = trait["dataSourceId"]
        # folderId = trait["folderId"]

        data_source = data_source_dict[dataSourceId]
        data_source_name = data_source["name"]
        segments_and_overlap_price = data_source["segments_and_overlap_price"]
        segments_and_overlap_uom = data_source["segments_and_overlap_uom"]
        modeling_price = data_source["modeling_price"]
        modeling_uom = data_source["modeling_uom"]
        activation_price = data_source["activation_price"]
        activation_uom = data_source["activation_uom"]

        segment_id_list.append(sid)
        segment_name_list.append(name)
        segment_description_list.append(description)
        segment_status_list.append(status)
        data_source_id_list.append(dataSourceId)
        data_source_name_list.append(data_source_name)
        segments_and_overlap_price_list.append(segments_and_overlap_price)
        segments_and_overlap_uom_list.append(segments_and_overlap_uom)
        modeling_price_list.append(modeling_price)
        modeling_uom_list.append(modeling_uom)
        activation_price_list.append(activation_price)
        activation_uom_list.append(activation_uom)

    write_df = pd.DataFrame({
                    "Segment ID":segment_id_list,
                    "Segment Name":segment_name_list,
                    "Segment Description":segment_description_list,
                    "Segment Status":segment_status_list,
                    "Data Source ID":data_source_id_list,
                    "Data Source Name":data_source_name_list,
                    "Segments and Overlap Price":segments_and_overlap_price_list,
                    "Segments and Overlap UoM":segments_and_overlap_uom_list,
                    "Modeling Price":modeling_price_list,
                    "Modeling UoM":modeling_uom_list,
                    "Activation Price":activation_price_list,
                    "Activation UoM":activation_uom_list
                })
    return write_excel.write(write_df, "DONOTUPLOAD_AdobeAAM_query_all")
    
def read_all_to_add_segments(file_path):
    data_source_name_dict = get_data_source_name_dict()

    read_df = None
    try:
        # Skip row 2 ([1]) tha indicates if field is mandatory or not
        read_df = pd.read_excel(file_path, sheet_name="Adobe AAM", skiprows=[1])
    except:
        return {"message":"File Path '{}' is not found".format(file_path)}
    
    segment_id_list = []
    segment_name_list = read_df["Segment Name"]
    segment_description_list = read_df["Segment Description"]
    segment_status_list = []
    data_source_id_list = []
    data_source_name_list = read_df["Data Source Name"]
    segments_and_overlap_price_list = read_df["Segments and Overlap Price"]
    segments_and_overlap_uom_list = []
    modeling_price_list = read_df["Modeling Price"]
    modeling_uom_list = read_df["Modeling UoM"]
    activation_price_list = read_df["Activation Price"]
    activation_uom_list = read_df["Activation UoM"]
    data_source_result = []

    # if name not in dict, add data source, append data source to dict (lowercase name: data source id)
    data_source_name_dict = get_data_source_name_dict()
    for data_source_name in data_source_name_list:
        lowercase_data_source_name = data_source_name.lower()
        
        data_source_id = None
        if lowercase_data_source_name in data_source_name_dict:
            data_source_id = data_source_name_dict[lowercase_data_source_name]
            data_source_result.append("OK")
        else:
            # Add case sensitive name for data source
            add_data_source_status, data_source_id = add_data_source(None, data_source_name)
            # Append lower case name to data source name dict
            data_source_name_dict[lowercase_data_source_name] = data_source_id
            data_source_result.append(add_data_source_status)

            print("Add Data Source Status: {}".format(add_data_source_status))
            print("New Data Source ID: {}".format(data_source_id))

        data_source_id_list.append(data_source_id)

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    write_df = pd.DataFrame({
                    "Data Source ID":data_source_id_list,
                    "Data Source Name":data_source_name_list,
                    "Data Source Result":data_source_result
                })
    return write_excel.write(write_df, file_name + "_output_add_segments")