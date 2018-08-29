import pandas as pd
import variables
from datetime import datetime

OUTPUT_PATH = variables.RETURN_FOLDER + "/"

def write(write_df, platform):
    current_date = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_name = platform + "_" + current_date + ".xlsx"
    writer = pd.ExcelWriter(OUTPUT_PATH + file_name)
    write_df.to_excel(writer,'Sheet1',index=False)
    writer.save()

    return {"file":file_name}