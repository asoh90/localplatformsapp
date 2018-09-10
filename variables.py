SECRET_KEY = 'a1ac33ec538de1e200d5f537e717ae6b'
UPLOAD_FOLDER = "upload"
RETURN_FOLDER = "to_return"

login_credentials = {}

platform_functions = {
                        "--Select Platform--":[],
                        "AppNexus": {"level":2,
                                    "functions": {
                                        "Segments":["Add Segments","Edit Segments","Query All Segments"],
                                        "Segments Troubleshoot":["Add Existing Segments to Specific Buyer Member","Retrieve Segment IDs","Retrieve Buyer Member Segments"],
                                        "Segment Billings":["Add Segment Billings","Edit Segment Billings"]
                                        }
                                    },
                        "The Trade Desk": {"level":1,
                                            "functions":["Add","Edit","Query"]
                                        }
                    }

def read_credentials(input):
    input_list = input.split("|")

    for input_row in input_list:
        # print("input row: " + input_row)
        input_row_list = input_row.split(":")

        platform = input_row_list[0]
        key = input_row_list[1]
        value = input_row_list[2]

        if platform in login_credentials:
            login_credentials[platform][key] = value
        else:
            login_credentials[platform] = {key:value}

    # print(login_credentials)