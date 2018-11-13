import pandas as pd
import variables
from datetime import datetime
import zipfile

OUTPUT_PATH = variables.RETURN_FOLDER + "/"

def write(write_df, file_name):
    file_name = file_name + ".xlsx"
    writer = pd.ExcelWriter(OUTPUT_PATH + file_name)
    write_df.to_excel(writer,'Sheet1',index=False)
    writer.save()

    return {"message":"{} has been downloaded".format(file_name),
            "file":file_name}

def delete(file_path, file_name):
    file_list = [file for file in os.listdir(file_path) if return_file.endswith(".xlsx")]
    for return_file in return_filelist:
        if (return_file == file_name):
            os.remove(os.path.join(RETURN_FOLDER, return_file))

def write_without_return(write_df, file_name):
    file_name = file_name + ".xlsx"
    writer = pd.ExcelWriter(OUTPUT_PATH + file_name)
    write_df.to_excel(writer,'Sheet1',index=False)
    writer.save()

    # Returns with .xlsx extension, without OUTPUT_PATH
    return file_name

def write_zip_file(file_names, zipped_file_name):
    zipped_file_name = zipped_file_name + ".zip"
    zipf = zipfile.ZipFile(OUTPUT_PATH + zipped_file_name, 'w', zipfile.ZIP_DEFLATED)
    for file_name in file_names:
        file_name = OUTPUT_PATH + file_name
        zipf.write(file_name)
    zipf.close()

    return {"message":"{} has been downloaded".format(zipped_file_name),
            "file":zipped_file_name}

def return_single_file(file_name):
    # file name from write_without_return should have .xlsx extension, but without OUTPUT_PATH
    return {"message":"{} has been downloaded".format(file_name),
            "file":file_name}