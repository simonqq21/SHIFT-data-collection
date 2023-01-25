try:
    import os
    from time import sleep 
    import json 
    from datetime import datetime, date, time, timedelta
    import pandas as pd 
except Exception as e:
    print(e)

from config import *
csv_filepath = "./"
csv_filename = "test.csv" 

def processDataForPublish(datetime, type, index, rawsensordata):
    global debug
    global expt_num, sitename
    data = csv_data
    data["datetime"] = [datetime]
    data["expt_num"] = [expt_num]
    data["sitename"]= [sitename]
    data["type"]= [type]
    data["index"]= [index]
    data["value"]= [rawsensordata]
    df = pd.DataFrame(data, columns=columns)
    if debug:
        print(df)
    return df 

def saveAndPublishData(df):
    print(df)
    print(df.to_json())
    df.to_csv(csv_filepath + csv_filename, mode='a', index=False, header=False)

# create csv file if it doesnt exist 
df = pd.DataFrame.from_dict(csv_data, orient='columns')
mode = 'w'
index=False
header=True
if os.path.exists(csv_filepath + csv_filename):
    mode = 'a'
    header=False
    print('exists!')
df.to_csv(csv_filepath + csv_filename, mode=mode, index=index, header=header)
columns = df.columns.values
print(columns)

df = processDataForPublish(datetime.now(), suffix_temperature, 0, 25.5)
saveAndPublishData(df)
# try:
#     client.publish(sensorPublishTopic, jsonData)
# except:
#     print("Publish failed, check broker")
