import requests
import variables
import json
import write_excel
import pandas as pd
import os
import numpy
import time

#Authentication credentials
CLIENT_ID = 'amzn1.application-oa2-client.3d27708f06da425bae2f82013fe0276a'
CLIENT_SECRET = 'e39517559810f15ce660205fa677e8eb8dce87ce371fe158981171244e0cb6b2'

SB_AUTHORIZATION_CODE='ANxnHqbiCvQewySSybXe'
SB_REFRESH_TOKEN = 'Atzr|IwEBIGDfXc18VLS7ojmb1KEsMdocay_FwMnnlkXy4y24vM0Dsd0g6kfT3aKKEFubV-pdsAQB3uF-58H16beqKvciAZFwxev6h1VqVgEzeFxo-n9vf-rwtViLIAh2HY8tJgu37ZrHSQApoofIjZH0skpJDMO160dD6J7daO0ieRAaTXosKUULiB4IXiORGRzfQIam6OncZvD9_MBuax1vsU-2dofGXVcd7BzL6kUaFryoGVVQoVQWAGcE-LKybwsKyHYuTYXof2ST0B6VGByjTicyeDwB1BhkeFGBPOIwb6w8AJragVQptGBQRkwx1vTZMw-pOqEAaCaX0T1r-1q-iJ1iwtuf7sDOP3SjQxw5A18rT9Nd4dl7Ocl2G9eio0K7ve-QeVaqHkzRBTU0qaGk3wXWYCK5'
#ACCESS_TOKEN = 'Atza|IwEBINw4Ymo8_9i8L9vUp28Y_uhbjy4N7bbplGPYgXzw9RLkPeImfxa2cvrzWE5RNU9S4TrMFfHnkMMjU3ON8KaVoc1X-sz2S030KWJ57G6TrNgguNmqT8Pw5h6DCfDaCoLVhIM4vnLCrZprVcZ_9KCOmCwxgQDeVECqXahKCTadLjOjruMFi5DYeBUBtAfPrvcfBFnH9hC6UXCKA_T8ZNt4L66JYg7_sJ2Y2GK1oxthFnR8S_tfteHxx7v9vgV4tbgyXf93pTmR81vDTjWgSnbiJeG7McSeW9ZzIDJrPAIAO3hYvOSnpW2CAWajO-m6ozxCcrL8w0LQ1oT0CArQXjbmgAmTqattOax56WvczAt0QIdO7ZhHL82smc_4319bL2MJVyx-Z5oJ9HBqsIkqHotWxID7Bu6ZbNZ6_t60QazV3fPcZg'

GRANT_TYPE='authorization_code'
REDIRECT_URI='http://127.0.0.1:5000/home'
CONTENT_TYPE='application/x-www-form-urlencoded'
CHARSET='UTF-8'

NA_AUTHORIZATION_CODE='ANBHpTEHEYsPupBAFigj'
EU_AUTHORIZATION_CODE='RHviVGtMKOGjEGpHIVsz'
FE_AUTHORIZATION_CODE='SReksMBQhyjxeXqFckPv'

NA_REFRESH_TOKEN='Atzr|IwEBIIyzKg45ArWQ7wnrB4yhCUJ61FRkXCjFT1EK_eXrJ2bz184_IjC_bIevd0fbrovG1AA7H4HP9dLiNkeHUrwE_qjw9dNpwcvmkErD4FOpoHMAHsY6Y2XuySBxTNA3Da9hGXlR6puoAwmv82fiVmQ_IcsZFoi4iwJw8Esc-P-Oh_hrePok-y2psNRFsELWCO73EIUy3nr8XbyzEL1yacpmLgqkx-sZYn7i6dzz-OLGS4mlQu1SdXznlZobH5juG3V6bEDLWuzsW4e__suSxf2aIBbQJv7m8dfHj50YudXAfDzLES7M38yf1JfazOZzGXL3i-aAWWtooOb1PDIAoz3rDVnJW9Yi0RTqeOP4KmIb9MEJMeScgXtSZI57ZvtZEI_dKpH7ZV6vvvnPcOvldKJokRj8'
EU_REFRESH_TOKEN='Atzr|IwEBIMBaeVZ4QRvkgMKqH53JQWnksbh9D6sRCF2Phz-Atbr-aWAsdBpPwcVVYqpTR_HxXPIGfQNNX134jRTrGbSM53WQcDm3ytSEeodttQ4I-EvT-mu4qdkeN9qjANhpiReijkfozYb_FkJeCktl_sUgVjxF6qYoD9oLAkJvCnAQBGbniiZ3AOywxgIiE9gJwo-YbAjarKGkXFKDcXdEL-R87DNjEjSH2kFKYuhvmF5OERuo6ozvK7Dhvfyqk6Y8JBrxh6rd6QkF0SyAOMh0qWyft-6phZJl9Tw02SbigNuXazLPuJ45latzTnr3bR58Voak67nV2b1eS7EYEQYeGsUbtayFlW4J5j9MYHCAmdNIjgiW1ctiS2uTSPOIOPaIog6U-EC__KHwQ7CAJLXXTMTdzAT9'
FE_REFRESH_TOKEN='Atzr|IwEBIFoNJboLzC4Vws_4QqyqaR_QVk7eULoKGsCfWPprxfcIPpmafqQUqFlc5evpZhPFU1we6EzvJ-wtyRIjrC3j0Y_1V5ceC93l7p1cNfPqtq083VYBk918NAm22E9O2dWtq9p-SZuidiTlRUXOQ5Ti0dpjQKuXIFXRUUec_KGXDXOkF9K8VcJpcr5yDXlePJhidoZT9dvmTignmJaakFecnbqBqEZYQBhpwXWoUuakMUrSN4Vu50Jeocn1KYpa02fv_rCKLEfJ3GUnauzfg_649ICnO1H3XjpHrhI8_lFpBidFR88YBo0wC3QCRybpP1NoczJTN3L0EBDeTDoY46daey6L2b6ksG68QjgotaYUDM4JAAyruR7LRl1e3pZD1KDdzTB_ejz4qfzZunCky8QIkt2w'

NA_API_SCOPE='3078478729532788'
EU_API_SCOPE='3562396754165501'
FE_API_SCOPE='1473057051413929'

auth_NA_url = 'https://api.amazon.com/auth/o2/token'
auth_EU_url = 'https://api.amazon.co.uk/auth/o2/token'
auth_FE_url = 'https://api.amazon.co.jp/auth/o2/token'

SANDBOX_URL = 'https://advertising-api-test.amazon.com'
API_NA_url = 'https://advertising-api.amazon.com'
API_EU_url = 'https://advertising-api-eu.amazon.com'
API_FE_url= 'https://advertising-api-fe.amazon.com'

test_US_advertiser= '1407654960901'
test_CA_advertiser= '2556642380601'
test_DE_advertiser= '8595642440102'
test_FR_advertiser= '3196829270502'
test_UK_advertiser= '7709340060402'
test_AU_advertiser= '9497467170803'
test_JP_advertiser= '6259435010103'

#url_segment = SANDBOX_URL + '/v2/dp/audiencemetadata'

SHEET_NAME = "Amazon"

def authenticate():
    data = {
                'grant_type':GRANT_TYPE,
                'code':AUTHORIZATION_CODE,
                'redirect_uri':REDIRECT_URI,
                'client_id':CLIENT_ID,
                'client_secret':CLIENT_SECRET
            }
    auth_json = requests.post(auth_NA_url,
                            headers={
                                'Content-Type':CONTENT_TYPE,
                                'charset':CHARSET
                            },
                            data=data).json()
    ACCESS_TOKEN = auth_json["access_token"]
    REFRESH_TOKEN = auth_json["refresh_token"]
    #auth tokens are valid for 60min and must refresh with refresh token once they expire
    return ACCESS_TOKEN, REFRESH_TOKEN

#refresh token after it expires
def refresh(REFRESH_TOKEN):
    data = {
                'grant_type':'refresh_token',
                'refresh_token':REFRESH_TOKEN,
                'client_id':CLIENT_ID,
                'client_secret':CLIENT_SECRET
            }
    refresh_json = requests.post(auth_NA_url,
                            headers={
                                'Content-Type':CONTENT_TYPE,
                                'charset':CHARSET
                            },
                            data=data).json()
    ACCESS_TOKEN = refresh_json["access_token"]
    return ACCESS_TOKEN

def callAPI(platform, function, file_path):
    
    start_time = time.time()


    if function == "Query All Segments":
        output = query_all_segments()
    else:
        # Check if SHEET_NAME exists in uploaded file
        try:
            read_df = pd.read_excel(file_path, sheet_name=SHEET_NAME, skiprows=[1])
        except:
            return{'message':"ERROR: Unable to find sheet name: {}".format(SHEET_NAME)}

        if function == "Add Segments":
            output = read_file_to_add_segments(file_path,platform)
        elif function == "Edit Segments":
            output = read_file_to_edit_segments(file_path,platform)
        elif function == "Retrieve Audience Size":
            output = read_file_to_retrieve_size(file_path,platform)

    elapsed_time = time.time() - start_time
    elapsed_mins = int(elapsed_time/60)
    elapsed_secs = int(elapsed_time%60)

    print("Elapsed time: {} mins {} secs".format(elapsed_mins, elapsed_secs))

    return output

def read_file_to_add_segments(file_path,platform):
    read_df = pd.read_excel(file_path, sheet_name=SHEET_NAME, skiprows=[1])

    segment_name_list = read_df["Segment Name"]
    segment_description_list = read_df["Segment Description"]
    price_list = read_df["Price"]
    duration_list = read_df["Duration"]
    segment_key_list = read_df["Segment Key"]
    advertiser_id_list = read_df["Advertiser ID"]

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    write_segment_name_list = []
    write_segment_description_list = []
    write_segment_price_list = []
    write_segment_duration_list = []
    write_segment_key_list = []
    write_segment_amazonid_list = []
    write_segment_advertiserid_list = []
    write_response = []

    add_segment_row_num = 0
    while add_segment_row_num < len(segment_name_list):
        current_segment_dict = {
            "segment_name":segment_name_list[add_segment_row_num],
            "segment_desc":segment_description_list[add_segment_row_num],
            "CPM":price_list[add_segment_row_num],
            "lifetime":duration_list[add_segment_row_num],
            "segment_key":segment_key_list[add_segment_row_num],
            "advertiser_id":advertiser_id_list[add_segment_row_num]
        }
        #add segments via api
        add_response = add_segment(current_segment_dict,platform)

        try:
            audience = add_response['audience']
            metadata = audience['metadata']
            fees = metadata['audienceFees'][0]
            print(audience['id'])
            amazonid = "id='" + str(audience['id']) + "'"
            write_segment_amazonid_list.append(amazonid)
            write_segment_name_list.append(audience['name'])
            write_segment_description_list.append(audience['description'])
            write_segment_advertiserid_list.append(audience['advertiserId'])
            write_segment_price_list.append(fees['cpmCents'])
            write_segment_duration_list.append(metadata['ttl'])
            write_segment_key_list.append(metadata['externalAudienceId'])
            write_response.append("Added")

        except:
            error_list = add_response['error']
            print(error_list)
            write_segment_amazonid_list.append("")
            write_segment_name_list.append(segment_name_list[add_segment_row_num])
            write_segment_description_list.append(segment_description_list[add_segment_row_num])
            write_segment_price_list.append(price_list[add_segment_row_num])
            write_segment_duration_list.append(duration_list[add_segment_row_num])
            write_segment_key_list.append(segment_key_list[add_segment_row_num])
            write_response.append("Error while adding segment")
        add_segment_row_num += 1

    write_df = pd.DataFrame({
                    "Amazon ID":write_segment_amazonid_list,
                    'Segment Name':write_segment_name_list,
                    'Segment Description':write_segment_description_list,
                    'Segment Key':write_segment_key_list,
                    'Price':write_segment_price_list,
                    'Duration':write_segment_duration_list,
                    'Advertiser ID':write_segment_advertiserid_list,
                    'Add Segment Response':write_response,
                })

    return write_excel.write(write_df, file_name + "_output_add_segments")
    

def read_file_to_edit_segments(file_path,platform):
    read_df = pd.read_excel(file_path, sheet_name=SHEET_NAME, skiprows=[1])

    amazonID_list = read_df["Amazon ID"]
    segment_description_list = read_df["Segment Description"]
    price_list = read_df["Price"]
    duration_list = read_df["Duration"]
    segment_key_list = read_df["Segment Key"]
    advertiser_id_list = read_df["Advertiser ID"]

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    write_segment_name_list = []
    write_segment_description_list = []
    write_segment_price_list = []
    write_segment_duration_list = []
    write_segment_key_list = []
    write_segment_amazonid_list = []
    write_segment_advertiserid_list = []
    write_response = []

    edit_segment_row_num = 0
    while edit_segment_row_num < len(amazonID_list):
        current_segment_dict = {
            "segment_desc":segment_description_list[edit_segment_row_num],
            "CPM":price_list[edit_segment_row_num],
            "lifetime":duration_list[edit_segment_row_num],
            "segment_key":segment_key_list[edit_segment_row_num],
            "amazon_ID":amazonID_list[edit_segment_row_num]

        }
        edit_response = edit_segment(current_segment_dict,platform)

        try:
            audience = edit_response['audience']
            metadata = audience['metadata']
            fees = metadata['audienceFees'][0]
            amazon_id = "id='" + str(audience['id']) + "'"
            write_segment_amazonid_list.append(amazon_id)
            write_segment_name_list.append(audience['name'])
            write_segment_description_list.append(audience['description'])
            write_segment_price_list.append(fees['cpmCents'])
            write_segment_duration_list.append(metadata['ttl'])
            write_segment_key_list.append(metadata['externalAudienceId'])
            write_segment_advertiserid_list.append(audience['advertiserId'])
            write_response.append("Segment Updated")
            
        except Exception as e:
            print(e)
            error_list = edit_response['error']
            write_segment_amazonid_list.append(advertiser_id_list(edit_segment_row_num))
            write_segment_description_list.append(segment_description_list[edit_segment_row_num])
            write_segment_price_list.append(price_list[edit_segment_row_num])
            write_segment_duration_list.append(duration_list[edit_segment_row_num])
            write_segment_key_list.append(segment_key_list[edit_segment_row_num])
            write_response.append("Error while editing segment")
        edit_segment_row_num += 1

    write_df = pd.DataFrame({
                    "Amazon ID":write_segment_amazonid_list,
                    'Segment Name':write_segment_name_list,
                    'Segment Description':write_segment_description_list,
                    'Segment Key':write_segment_key_list,
                    'Price':write_segment_price_list,
                    'Duration':write_segment_duration_list,
                    'Advertiser ID':write_segment_advertiserid_list,
                    'Edit Segment Response':write_response,
                })

    return write_excel.write(write_df, file_name + "_output_edit_segments")

def read_file_to_retrieve_size(file_path,platform):
    read_df = pd.read_excel(file_path, sheet_name=SHEET_NAME, skiprows=[1])

    amazonID_list = read_df["Amazon ID"]

    os.remove(file_path)
    file_name_with_extension = file_path.split("/")[-1]
    file_name = file_name_with_extension.split(".xlsx")[0]

    write_segment_name_list = []
    write_segment_description_list = []
    write_segment_price_list = []
    write_segment_duration_list = []
    write_segment_key_list = []
    write_segment_amazonid_list = []
    write_segment_advertiserid_list = []
    write_segment_receivedAudienceSize_list = []
    write_segment_matchedAudienceSize_list = []
    write_segment_matchRate = []
    write_response = []

    get_segment_row_num = 0
    while get_segment_row_num < len(amazonID_list):
        current_segment_dict = {
            "AmazonID":amazonID_list[get_segment_row_num],
        }
        #get segments via api
        get_response = get_segment(current_segment_dict,platform)

        try:
            audience = get_response['audience']
            metadata = audience['metadata']
            fees = metadata['audienceFees'][0]
            size = metadata['audienceSize']
            print(audience['id'])
            amazonid = "id='" + str(audience['id']) + "'"
            write_segment_amazonid_list.append(amazonid)
            write_segment_name_list.append(audience['name'])
            write_segment_description_list.append(audience['description'])
            write_segment_advertiserid_list.append(audience['advertiserId'])
            write_segment_price_list.append(fees['cpmCents'])
            write_segment_duration_list.append(metadata['ttl'])
            write_segment_key_list.append(metadata['externalAudienceId'])
            audienceSize = "s'" + str(size['receivedAudienceSize']) + "'"
            write_segment_receivedAudienceSize_list.append(audienceSize)
            matchedSize = "s'" + str(size['matchedAudienceSize']) + "'"
            write_segment_matchedAudienceSize_list.append(matchedSize)
            matchRate = "s'" + str(size['matchRate']) + "'"
            write_segment_matchRate.append(matchRate)
            write_response.append("OK")

        except:
            error_list = get_response['error']
            print(error_list)
            write_segment_amazonid_list.append(amazonID_list[get_segment_row_num])
            write_segment_name_list.append("")
            write_segment_description_list.append("")
            write_segment_advertiserid_list.append("")
            write_segment_price_list.append("")
            write_segment_duration_list.append("")
            write_segment_key_list.append("")
            write_segment_receivedAudienceSize_list.append("")
            write_segment_matchedAudienceSize_list.append("")
            write_segment_matchRate.append("")
            write_response.append("Error while retrieving segment")
        get_segment_row_num += 1

    write_df = pd.DataFrame({
                    "Amazon ID":write_segment_amazonid_list,
                    'Segment Name':write_segment_name_list,
                    'Segment Description':write_segment_description_list,
                    'Segment Key':write_segment_key_list,
                    'Price':write_segment_price_list,
                    'Duration':write_segment_duration_list,
                    'Advertiser ID':write_segment_advertiserid_list,
                    'Received Audience Size':write_segment_receivedAudienceSize_list,
                    'Matched Audience Size':write_segment_matchedAudienceSize_list,
                    'Match Rate':write_segment_matchRate,
                    'Add Segment Response':write_response,
                })

    return write_excel.write(write_df, file_name + "_output_audienceSize")


def add_segment(segment_dict,platform):
    response = "Error before calling Add Request API, please ensure duration is in numbers and price is in numbers or decimals."
    ACCESS_TOKEN = ""
    url_segment = ""
    API_SCOPE = ""
    currency = ""
    if platform == "Amazon Staging":
        ACCESS_TOKEN = refresh(SB_REFRESH_TOKEN)
        url_segment = SANDBOX_URL + '/v2/dp/audiencemetadata'
        API_SCOPE = "2220556679185588"
        currency = "USD"
    elif platform == "Amazon NA":
        ACCESS_TOKEN = refresh(NA_REFRESH_TOKEN)
        url_segment = API_NA_url + '/v2/dp/audiencemetadata'
        API_SCOPE = NA_API_SCOPE
        currency = "USD"
    elif platform == "Amazon EU":
        ACCESS_TOKEN = refresh(EU_REFRESH_TOKEN)
        url_segment = API_EU_url + '/v2/dp/audiencemetadata'
        API_SCOPE = EU_API_SCOPE
        currency = "GBP"
    elif platform == "Amazon FE":
        ACCESS_TOKEN = refresh(FE_REFRESH_TOKEN)
        url_segment = API_FE_url + '/v2/dp/audiencemetadata'
        API_SCOPE = FE_API_SCOPE
        currency = "JPY"


    try:
        segment_to_add = {
                            "name": str(segment_dict['segment_name']),
                            "description": str(segment_dict['segment_desc']),
                            "advertiserId": str(segment_dict['advertiser_id']),
                            "metadata": {
                                "type": "DATA_PROVIDER",
                                "ttl": int(segment_dict['lifetime']),
                                "externalAudienceId": str(segment_dict['segment_key']),
                                "audienceFees": [
                                    {
                                        "cpmCents": int(segment_dict['CPM']),
                                        "currency": currency
                                    }
                                ]
                            }
                        }

        request_to_send = requests.post(url_segment,
                                    headers={
                                        'Content-Type':'application/json',
                                        'Amazon-Advertising-API-ClientID':CLIENT_ID,
                                        'Amazon-Advertising-API-Scope':API_SCOPE,
                                        'Authorization':'Bearer ' + ACCESS_TOKEN
                                    },
                                    json=segment_to_add)
    except Exception as e:
        print(e)

    print("Add Request: " + request_to_send.url)
    print(ACCESS_TOKEN)
    add_response = request_to_send.json()

    return add_response

def edit_segment(segment_dict,platform):
    response = "Error before calling Add Request API, please ensure duration is in numbers and price is in numbers or decimals."
    ACCESS_TOKEN = ""
    url_segment = ""
    API_SCOPE = ""
    currency = ""
    if platform == "Amazon Staging":
        ACCESS_TOKEN = refresh(SB_REFRESH_TOKEN)
        url_segment = SANDBOX_URL + '/v2/dp/audiencemetadata'
        API_SCOPE = "2220556679185588"
        currency = "USD"
    elif platform == "Amazon NA":
        ACCESS_TOKEN = refresh(NA_REFRESH_TOKEN)
        url_segment = API_NA_url + '/v2/dp/audiencemetadata'
        API_SCOPE = NA_API_SCOPE
        currency = "USD"
    elif platform == "Amazon EU":
        ACCESS_TOKEN = refresh(EU_REFRESH_TOKEN)
        url_segment = API_EU_url + '/v2/dp/audiencemetadata'
        API_SCOPE = EU_API_SCOPE
        currency = "GBP"
    elif platform == "Amazon FE":
        ACCESS_TOKEN = refresh(FE_REFRESH_TOKEN)
        url_segment = API_FE_url + '/v2/dp/audiencemetadata'
        API_SCOPE = FE_API_SCOPE
        currency = "JPY"
    try:
        print("reaches line 444")
        segment_to_edit = {
                            "description": str(segment_dict['segment_desc']),
                            "metadata": {
                                "ttl": int(segment_dict['lifetime']),
                                "audienceFees": [
                                    {
                                        "cpmCents": int(segment_dict['CPM']),
                                        "currency": currency
                                    }
                                ]
                            }
                        }
        amazon_id_raw = segment_dict["amazon_ID"]
        amazon_id_cleaned = amazon_id_raw[4:(len(amazon_id_raw)-1)]             
        print(amazon_id_cleaned)
        url_edit_segment = url_segment + "/" + str(amazon_id_cleaned)
        print("reaches line 461")
        request_to_send = requests.put(url_edit_segment,
                                    headers={
                                        'Accept':"*/*",
                                        'Content-Type':'application/json',
                                        'Amazon-Advertising-API-ClientID':CLIENT_ID,
                                        'Amazon-Advertising-API-Scope':API_SCOPE,
                                        'Authorization':ACCESS_TOKEN
                                    },
                                    json=segment_to_edit)
    except Exception as e:
        print(e)
    print("Edit Request: " + request_to_send.url)
    edit_response = request_to_send.json()
    print(ACCESS_TOKEN)
    print(edit_response)

    return edit_response

def get_segment(segment_dict,platform):
    response = "Error before calling Add Request API, please ensure duration is in numbers and price is in numbers or decimals."
    ACCESS_TOKEN = ""
    url_segment = ""
    API_SCOPE = ""
    currency = ""
    if platform == "Amazon Staging":
        ACCESS_TOKEN = refresh(SB_REFRESH_TOKEN)
        url_segment = SANDBOX_URL + '/v2/dp/audiencemetadata'
        API_SCOPE = "2220556679185588"
        currency = "USD"
    elif platform == "Amazon NA":
        ACCESS_TOKEN = refresh(NA_REFRESH_TOKEN)
        url_segment = API_NA_url + '/v2/dp/audiencemetadata'
        API_SCOPE = NA_API_SCOPE
        currency = "USD"
    elif platform == "Amazon EU":
        ACCESS_TOKEN = refresh(EU_REFRESH_TOKEN)
        url_segment = API_EU_url + '/v2/dp/audiencemetadata'
        API_SCOPE = EU_API_SCOPE
        currency = "GBP"
    elif platform == "Amazon FE":
        ACCESS_TOKEN = refresh(FE_REFRESH_TOKEN)
        url_segment = API_FE_url + '/v2/dp/audiencemetadata'
        API_SCOPE = FE_API_SCOPE
        currency = "JPY"


    try:
        amazon_id_raw = segment_dict["AmazonID"]
        amazon_id_cleaned = amazon_id_raw[4:(len(amazon_id_raw)-1)]             
        print(amazon_id_cleaned)
        url_segment = url_segment + "/" + str(amazon_id_cleaned)
        request_to_send = requests.get(url_segment,
                                    headers={
                                        'Accept':"*/*",
                                        'Content-Type':"application/json",
                                        'Amazon-Advertising-API-ClientID':CLIENT_ID,
                                        'Amazon-Advertising-API-Scope':API_SCOPE,
                                        'Authorization':ACCESS_TOKEN
                                    })
        #print(CLIENT_ID)
        #print(API_SCOPE)
        #print(ACCESS_TOKEN)
        #print(request_to_send.headers)
    except Exception as e:
        #print(response)
        print(e)

    print("Get Request: " + request_to_send.url)
    get_response = request_to_send.json()
    print(get_response)

    return get_response