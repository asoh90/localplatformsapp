import pandas as pd
from datetime import datetime

OUTPUT_PATH = "to_return/"

def write(write_df, platform):
    current_date = datetime.now().strftime("%Y-%m-%d %H;%M;%S")
    file_name = OUTPUT_PATH + platform + "_" + current_date + ".xlsx"
    writer = pd.ExcelWriter(file_name)
    write_df.to_excel(writer,'Sheet1',index=False)
    writer.save()

    return {"message":"{} is ready for download".format(file_name),
            "file":file_name}