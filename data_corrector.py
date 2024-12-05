# To run this file, use this on terminal : 
# python data_corrector.py

# To log the output onto a text file, use the below prompt : 
# python data_corrector.py > DataProcessorOutputLog.txt

import json
from tqdm import tqdm
from distance_corrector import *
from date_corrector import *

source_file_path = '.\Dataset\Dataset.json'
target_file_path = '.\Dataset\Dataset_processed.json'

def check_invalid_entries(data):
    invalid_keys = []
    ref_keys = list(data[0].keys())
    for entry in tqdm(data, desc='Checking data for invlid entries'):
        for key in ref_keys:
            value = str(entry[key]).strip()
            if (len(value)==0 or value in ('none','null','empty')) and (key not in invalid_keys):
                invalid_keys.append(key)
    print("Keys with invalid data : ",invalid_keys)

def check_invalid_key_combinations(data):
    invalid_combinations = []
    # ref_keys = list(data[0].keys())
    ref_keys = ['FromISO', 'FromZipCode', 'ToISO', 'ToZipCode', 'ForwardingAgentName', 'LoadingDate', 'UnloadingDate', 'OriginalETA', 'DeliveryDate', 'CO2', 'TotalTransportCost', 'NumberOfPieces', 'MeansOfTransport', 'Agreement', 'Distance', 'Weight', 'Agent']
    for entry in tqdm(data, desc="Checking data for combinations of invalid keys"):
        current_combo = ''
        for key in ref_keys:
            value = str(entry[key]).strip()
            if (value=='0' or len(value)==0 or value in ('none','null','empty')) and (key not in current_combo):
                current_combo = current_combo+' : '+key
        temp_flag = False
        for item in invalid_combinations:
            temp_key = list(item.keys())[0]
            if temp_key==current_combo:
                item[temp_key] = item[temp_key]+1
                temp_flag = True
        if temp_flag==False:
            invalid_combinations.append({current_combo: 0})
    print("Present entries with multiple invalid entry values : ")
    for item in invalid_combinations:
        print(str(item).replace('}','').replace('{',''))

def drop_invalid_entries(data, key:str):
    new_data = []
    for entry in tqdm(data, desc=("Dropping invalid entries based on "+key)):
        value = str(entry[key]).strip().lower()
        if len(value)!=0 and value not in ('none','null'):
            new_data.append(entry)
    
def print_categories(data, key: str):
    categories = []
    for entry in data:
        value = str(entry[key]).strip()
        if value not in categories:
            categories.append(value)
    print("Categories of data for key ",key," : ",categories,'\n')

def get_raw_data():
    with open(source_file_path, 'r') as file:
        data = json.load(file)
        keys = data[0].keys()
        print("\nKeys in loaded data : ", str(keys).replace(']','').replace('[',''),'\n')
        return data

def write_processed_data(data):
    with open(target_file_path, 'w+') as target_file:
        json.dump(data, target_file, indent=4)
    target_file.close()
    print("Processed Data written to file ",target_file_path)

def drop_final_invalid_data(data):
    ref_keys = ['LoadingDate', 'UnloadingDate', 'DeliveryDate', 'Distance']
    new_data = []
    for entry in tqdm(data, desc="Dropping invalid data after processing"):
        for key in ref_keys:
            value = str(entry[key]).lower()
            if len(value)>0 and (value not in ('none','null','empty','0','0.0')) and (entry not in new_data):   
                new_data.append(entry)
    dropped_count = len(new_data)-len(data)
    print(dropped_count," entries have been dropped from data")
    return new_data

data = get_raw_data()
check_invalid_entries(data)
check_invalid_key_combinations(data)
date_corrected = run_date_corrector(data)
distance_corrected = run_distance_corrector(date_corrected, include_MoT=True)
# Use this to correct distance data including MeansOfTransport as a factor
# distance_corrected = run_distance_corrector(date_corrected, include_MoT=True) 
check_invalid_entries(data)
check_invalid_key_combinations(data)
final_data = drop_final_invalid_data(data)
total_drop_count = (len(data)-len(final_data))
print('\n',total_drop_count,' entries dropped from data')
# Use this line to write processed data to a new Dataset_processed.json file
# write_processed_data(distance_corrected)