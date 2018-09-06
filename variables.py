SECRET_KEY = 'a1ac33ec538de1e200d5f537e717ae6b'
UPLOAD_FOLDER = "upload"
RETURN_FOLDER = "to_return"

login_credentials = {}

platform_functions = {
                        "--Select Platform--":[],
                        "AppNexus": ["add1","add2","add3"],
                        "The Trade Desk": ["Query","Add","Edit"]
                    };

def read_credentials(input):
    for input_row in input.split("|")
        for input_detail in input_row.split(":")
            platform = input_detail[0]
            key = input_detail[1]
            value = input_detail[2]

            login_credentials[platform] = {key:value}