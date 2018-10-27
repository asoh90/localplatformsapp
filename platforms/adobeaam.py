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

CONTENT_TYPE = "application/x-www-form-urlencoded"
AUTHORIZATION = "Basic ZXllb3RhLWJhYWFtOnJvZDZsOWluamRzZmwyN2E2cGUybjNsam50cmhndnRpM3A5NGN1YnUyMXVzdjZ2MXBicg=="
GRANT_TYPE = "password"

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

    if function == "Query":
        output = get_data_source()
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

def get_data_source():
    access_token = authenticate()

    get_data_source = requests.get(DATA_SOURCE_URL,
                            headers={
                                'Content-Type':"application/json",
                                'Authorization':"Bearer " + access_token
                            })
    print("Get Data Source URL: {}".format(get_data_source.url))

    data_source_json = get_data_source.json()
    data_source_dict = {}

    # commented out all the unused parameters
    for data_source in data_source_json:
        pid = data_source["pid"]
        name = data_source["name"])
        description = data_source["description"]
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

    data_source_dict[dataSourceId] = {"name":name, }
    return data_source_dict

    def get_data_feed(access_token, data_source_id):
        get_data_feed = requests.get(DATA_FEED_URL.format(data_source_id),
                            headers={
                                'Content-Type':"application/json",
                                'Authorization':"Bearer " + access_token
                            }))
        data_feed_json = get_data_feed.json()
        for data_feed in data_feed_json:
            planId = data_feed_json("planId")
            dataSourceId = data_feed_json("dataSourceId")
            description = data_feed_json("description")
            useCase = data_feed_json("")
            "planId": 422,
            "dataSourceId": 38623,
            "description": "",
            "useCase": [
                "SEGMENTS_AND_OVERLAP"
            ],
            "status": "ACTIVE",
            "billingCycle": "MONTHLY_IN_ARREARS",
            "billingUnit": "FIXED",
            "price": 0,
            "createTime": 1446115929000,
            "updateTime": 1446115929000,
            "crUID": 16260,
            "upUID": 16260