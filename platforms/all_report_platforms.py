import write_excel
import appnexus
import adform

ALL_REPORT_PLATFORMS_SHEET_NAME = "All Report Platforms"

def get_report(function, file_path):
    if function == "Data Usage Report":
        return get_data_usage_report(file_path)
    else:
        return {"message":"Error. No such function '{}'".format(function)}

def get_data_usage_report(file_path):
    # Adform get data usage report
    adform_file_names_output = adform.read_file_to_get_data_usage_report(file_path, ALL_REPORT_PLATFORMS_SHEET_NAME)

    # AppNexus get data usage report
    appnexus.get_urls("AppNexus")
    appnexus_segment_dict = appnexus.retrieve_all_segments()
    appnexus_file_names_output = appnexus.read_file_to_get_report(file_path, "data_usage", ALL_REPORT_PLATFORMS_SHEET_NAME, appnexus_segment_dict)

    # if "message" is in the output, it is an error message
    if "message" in adform_file_names_output:
        return adform_file_names_output
    elif "message" in appnexus_file_names_output:
        return appnexus_file_names_output
    else:
        file_names = adform_file_names_output + appnexus_file_names_output
        return write_excel.return_report(file_names, file_path)