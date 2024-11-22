import json
from tqdm import tqdm
from collections import Counter
from datetime import datetime, timedelta

filePath = ".\Dataset\Dataset.json"
targetFilePath = ".\Dataset\Dataset_1.json"
max_date = datetime(1900,1,1)
min_date = datetime.now()
today = datetime.now()
delivery_times = []
median_delivery = 0

def get_median_delivery_time(data):
    global median_delivery
    global delivery_times
    for entry in tqdm(data, desc="Get Median Delivery Time"):
        
        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")
        unloading_date_as_string = str(entry['UnloadingDate']).split('T')[0]
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d")

        delivery_time = abs((delivery_date-unloading_date).days)
        if delivery_time<50:
            delivery_times.append(delivery_time)
    counts = Counter(delivery_times)
    median_delivery = counts.most_common[0][0]

def get_max_min_dates(data):
    global max_date
    global min_date
    for entry in tqdm(data, desc="Getting Date Ranges"):
        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")
        if delivery_date>max_date and delivery_date<=today:
            max_date = delivery_date
        loading_date_as_string = str(entry['LoadingDate']).split('T')[0]
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d")
        if loading_date<min_date:
            min_date = loading_date
    print("Max Date in Dataset : ",max_date)
    print("Min Date in Dataset : ",min_date,'\n')

def replace_loading_unloading_outlier(data):
    for entry in tqdm(data, desc="Cleaning Loading and Unloading Dates"):
        
        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")
        loading_date_as_string = str(entry['LoadingDate'])
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%dT%H:%M:%S")
        unloading_date_as_string = str(entry['UnloadingDate'])
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%dT%H:%M:%S")

        if delivery_date.year>today.year:
            temp = datetime(today.year, loading_date.month, loading_date.day)
            # print("DeliveryDate update : ",delivery_date," -> ",temp)
            delivery_date = temp

        if unloading_date.year>today.year:
            temp = datetime(today.year, unloading_date.month, unloading_date.day, unloading_date.hour, unloading_date.minute, unloading_date.second)
            if delivery_date<=today and delivery_date.month>unloading_date.month:
                temp = datetime(delivery_date.year, unloading_date.month, unloading_date.day, unloading_date.hour, unloading_date.minute, unloading_date.second)
            # print("UnloadingDate update : ",unloading_date," -> ",temp)
            unloading_date = temp

        if loading_date.year>today.year:
            temp = datetime(today.year, loading_date.month, loading_date.day, loading_date.hour, loading_date.minute, loading_date.second)
            if delivery_date<=today and delivery_date.month>loading_date.month:
                temp = datetime(delivery_date.year, loading_date.month, loading_date.day, loading_date.hour, loading_date.minute, loading_date.second)
            # print("LoadingDate update : ",loading_date," -> ",temp,'\n')
            loading_date = temp

        entry['LoadingDate'] = str(loading_date).replace(" ",'T')
        entry['UnloadingDate'] = str(unloading_date).replace(" ",'T')
        entry['DeliveryDate'] = str(delivery_date).split(' ')[0]
    return data

def append_day(month, day):
    feb = 2
    lower = [4, 6, 9, 11]
    if month==feb and day>27:
        return 27
    if month in lower and day>30:
        return 30
    return day

def check_date(month, day):
    feb = 2
    lower = [4, 6, 9, 11]
    if month==feb and day>28:
        return False
    if month in lower and day>30:
        return False
    return True

def get_transport_ETA(means_of_transport):
    if means_of_transport=='air':
        return 7
    elif means_of_transport=='train':
        return 25
    elif means_of_transport=='sea':
        return 50
    elif means_of_transport=='truck':
        return 5
    elif 'container' in means_of_transport:
        return 2
    elif means_of_transport in ['courier','express']:
        return 2
    return 2

def fix_unload_before_load(data):
    for entry in tqdm(data, desc="Fixing Unloads before Loads"):

        transport = entry['MeansOfTransport']
        loading_date_as_string = str(entry['LoadingDate'])
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%dT%H:%M:%S")
        unloading_date_as_string = str(entry['UnloadingDate'])
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%dT%H:%M:%S")
        
        if unloading_date<loading_date:
            unloading_date = loading_date+timedelta(get_transport_ETA(transport.lower()))

        entry['LoadingDate'] = str(loading_date).replace(' ','T')
        entry['UnloadingDate'] = str(unloading_date).replace(' ','T')
    return data

def fix_deliv_before_unload(data):
    for entry in tqdm(data, desc="Fixing Delivery before Unloading"):
        
        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")
        unloading_date_as_string = str(entry['UnloadingDate'])
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%dT%H:%M:%S")

        if delivery_date<unloading_date:
            temp = unloading_date+timedelta(median_delivery)
            delivery_date = temp
        entry['DeliveryDate'] = str(delivery_date).split(' ')[0]
    return data

def print_date_flags(data):
    unload_lessthan_load = 0
    deliv_lessthan_unload = 0
    deliv_lessthan_load = 0
    for entry in data:
        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")
        loading_date_as_string = str(entry['LoadingDate'])
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%dT%H:%M:%S")
        unloading_date_as_string = str(entry['UnloadingDate'])
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%dT%H:%M:%S")
        if unloading_date<loading_date:
            unload_lessthan_load = unload_lessthan_load+1
        if delivery_date<unloading_date:
            deliv_lessthan_unload = deliv_lessthan_unload+1
        if delivery_date<loading_date:
            deliv_lessthan_load = deliv_lessthan_load+1
    print("\nUnload before Load : ",unload_lessthan_load)
    print("Delivery before Unload : ",deliv_lessthan_unload)
    print("Delivery before Load : ",deliv_lessthan_load,'\n')

with open(filePath, 'r') as file:
    data = json.load(file)
    get_max_min_dates(data)
    data = replace_loading_unloading_outlier(data)
    data = fix_unload_before_load(data)
    data = fix_deliv_before_unload(data)
    print_date_flags(data)
    with open(targetFilePath, "w") as json_file:
        json.dump(data, json_file, indent=4)