import pandas as pd
import variables
from datetime import datetime

OUTPUT_PATH = variables.RETURN_FOLDER + "/"

def write(write_df, platform):
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = platform + "_" + current_date + ".xlsx"
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