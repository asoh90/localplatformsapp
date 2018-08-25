import pandas as pd
from datetime import datetime

def write_excel(write_df, platform):
    current_date = datetime.now().strftime("%Y-%m-%d %H;%M;%S")
    writer = pd.ExcelWriter(platform + "_" + current_date + ".xlsx")
    write_df.to_excel(writer,'Sheet1',index=False)
    writer.save()