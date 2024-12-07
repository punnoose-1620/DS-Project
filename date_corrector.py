import json
from tqdm import tqdm
from collections import Counter
from datetime import datetime, timedelta, date

max_date = datetime(1900,1,1)
min_date = datetime.now()
today = datetime.now()
delivery_times = []
median_delivery = 0

def print_year_combos(data, tag=''):
    year_combos = []
    for entry in data:
        loading_date_as_string = str(entry['LoadingDate']).split('T')[0]
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d")
        
        unloading_date_as_string = str(entry['UnloadingDate']).split('T')[0]
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d")

        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")
        flag = ''
        if (delivery_date.year<unloading_date.year) or (delivery_date.year<loading_date.year) or (unloading_date.year<loading_date.year):
            flag = ' : INVALID'
        key = str(loading_date.year)+" :  "+str(unloading_date.year)+"  : "+str(delivery_date.year)+flag
        value = 0
        combo = {key: value}
        present = False
        for item in year_combos:
            temp_keys = list(item.keys())
            if key in temp_keys:
                present = True
                item[temp_keys[0]] = item[temp_keys[0]] +1
        if present==False:
            year_combos.append(combo)
    print("\nExisting combination of years ",tag,"\nLoad : Unload : Delivery : Validity(count)")
    invalid_count = 0
    for item in year_combos:
        keys = list(item.keys())[0]
        value = str(item[keys])
        if 'INVALID' in keys:
            invalid_count = invalid_count+int(value)
        print(keys,'(',value,')')
    print("Total Invalid Count : ",invalid_count)

def print_years(data, tag=''):
    loading_years = []
    unloading_years = []
    delivery_years = []
    for entry in data:
        loading_date_as_string = str(entry['LoadingDate']).split('T')[0]
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d")
        
        unloading_date_as_string = str(entry['UnloadingDate']).split('T')[0]
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d")

        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")

        if loading_date.year not in loading_years:
            loading_years.append(loading_date.year)
        if unloading_date.year not in unloading_years:
            unloading_years.append(unloading_date.year)
        if delivery_date.year not in delivery_years:
            delivery_years.append(delivery_date.year)
    
    print("\nCurrent list of years in data ",tag," : ")
    print("Loading Years : ", str(loading_years).replace(']','').replace('[',''))
    print("Unloading Years : ", str(unloading_years).replace(']','').replace('[',''))
    print("Delivery Years : ", str(delivery_years).replace(']','').replace('[',''))

def correct_year(data):
    print("\n")
    flag = False
    for entry in tqdm(data, desc="Correcting year typos"):
        loading_date_as_string = str(entry['LoadingDate']).split('T')[0]
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d")
        
        unloading_date_as_string = str(entry['UnloadingDate']).split('T')[0]
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d")

        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")
        
        if delivery_date>today:
            if loading_date.year==unloading_date.year or loading_date.year==(unloading_date.year-1):
                temp = datetime(unloading_date.year, delivery_date.month, delivery_date.day)
                if temp<=today:
                    delivery_date = temp
                    flag = True
                # else:
                #     print()
                # add condition to replace delivery date when temp>today
        elif unloading_date>today:
            if loading_date.year==delivery_date.year:
                temp = datetime(loading_date.year, unloading_date.month, unloading_date.day)
                if temp<=today:
                    unloading_date = temp
                    flag = True
                # else:
                #     print()
                # add condition to replace unloading date when temp>today
        elif loading_date>today:
            if unloading_date.year==delivery_date.year or unloading_date.year==(delivery_date.year-1):
                temp = datetime(unloading_date.year, loading_date.month, loading_date.day)
                if temp<=today:
                    loading_date = temp
                    flag = True
                # else:
                #     print()
                # add condition to replace delivery date when temp>today
        entry['LoadingDate'] = str(date(loading_date.year, loading_date.month, loading_date.day))
        entry['UnloadingDate'] = str(date(unloading_date.year, unloading_date.month, unloading_date.day))
        entry['DeliveryDate'] = str(date(delivery_date.year, delivery_date.month, delivery_date.day))
    if flag==False: 
        print("No Changes made while correcting year typos (1st round)....")
    return data

def correct_unload_load_switch(data):
    print("\n")
    flag = False
    for entry in tqdm(data, desc="Correcting switched loading and unloading dates"):
        loading_date_as_string = str(entry['LoadingDate']).split('T')[0]
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d")
        
        unloading_date_as_string = str(entry['UnloadingDate']).split('T')[0]
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d")

        if loading_date>unloading_date and loading_date<today and unloading_date<today:
            temp = loading_date
            loading_date = unloading_date
            unloading_date = temp
            flag = True
        entry['LoadingDate'] = str(date(loading_date.year, loading_date.month, loading_date.day))
        entry['UnloadingDate'] = str(date(unloading_date.year, unloading_date.month, unloading_date.day))
    if flag==False: 
        print("No Changes made while switching loading and unloading dates....")
    return data

def correct_unload_delivery_switch(data):
    flag = False
    for entry in tqdm(data, desc="Correcting switched unloading and delivery dates"):
        loading_date_as_string = str(entry['LoadingDate']).split('T')[0]
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d")
        
        unloading_date_as_string = str(entry['UnloadingDate']).split('T')[0]
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d")

        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")

        if delivery_date.year<unloading_date.year:
            if loading_date.year==delivery_date.year:
                entry['UnloadingDate'] = str(date(delivery_date.year, unloading_date.month, unloading_date.day))
                entry['DeliveryDate'] = str(date(unloading_date.year, delivery_date.month, delivery_date.day))
    return data

def correct_year_typing_typos(data):
    print("\n")
    flag = False
    for entry in tqdm(data, desc="Correcting additional typos after initial corrections"):
        loading_date_as_string = str(entry['LoadingDate']).split('T')[0]
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d")
        
        unloading_date_as_string = str(entry['UnloadingDate']).split('T')[0]
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d")

        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")

        if loading_date.year>today.year:
            year_as_string = str(loading_date.year)
            year_as_string = year_as_string[0]+year_as_string[2]+year_as_string[1]+year_as_string[3]
            year_as_int = int(year_as_string)
            if year_as_int<=today.year:
                loading_date = date(year_as_int, loading_date.month, loading_date.day)
                flag = True
        
        if unloading_date.year>today.year:
            year_as_string = str(unloading_date.year)
            year_as_string = year_as_string[0]+year_as_string[2]+year_as_string[1]+year_as_string[3]
            year_as_int = int(year_as_string)
            if year_as_int<=today.year:
                unloading_date = date(year_as_int, unloading_date.month, unloading_date.day)
                flag = True

        if delivery_date.year>today.year:
            year_as_string = str(delivery_date.year)
            year_as_string = year_as_string[0]+year_as_string[2]+year_as_string[1]+year_as_string[3]
            year_as_int = int(year_as_string)
            if year_as_int<=today.year:
                delivery_date = date(year_as_int, delivery_date.month, delivery_date.day)
                flag = True

        entry['LoadingDate'] = str(date(loading_date.year, loading_date.month, loading_date.day))
        entry['UnloadingDate'] = str(date(unloading_date.year, unloading_date.month, unloading_date.day))
        entry['DeliveryDate'] = str(date(delivery_date.year, delivery_date.month, delivery_date.day))
    if flag==False: 
        print("No Changes made while correcting year typos (2nd round)....")
    return data

def correct_year_anomalies(data):
    print("\n")
    flag = False
    for entry in tqdm(data, desc="Correcting delivery year anomalies based on delivery duration"):
        
        unloading_date_as_string = str(entry['UnloadingDate']).split('T')[0]
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d")

        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")

        if (delivery_date.year-unloading_date.year)>1 or (delivery_date.year-unloading_date.year)<-1:
            delivery_date = date(unloading_date.year, delivery_date.month, delivery_date.day)
            flag = True
        entry['DeliveryDate'] = str(date(delivery_date.year, delivery_date.month, delivery_date.day))
    if flag==False: 
        print("No Changes made while correcting year anomalies....")
    return data

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
    print("\n")
    flag = False
    for entry in tqdm(data, desc="Cleaning Loading and Unloading Dates"):
        
        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")
        loading_date_as_string = str(entry['LoadingDate'])
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d") #T%H:%M:%S
        unloading_date_as_string = str(entry['UnloadingDate'])
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d") #T%H:%M:%S

        if delivery_date.year>today.year:
            temp = datetime(today.year, loading_date.month, loading_date.day)
            delivery_date = temp
            flag = True

        if unloading_date.year>today.year:
            temp = datetime(today.year, unloading_date.month, unloading_date.day, unloading_date.hour, unloading_date.minute, unloading_date.second)
            if delivery_date<=today and delivery_date.month>unloading_date.month:
                temp = datetime(delivery_date.year, unloading_date.month, unloading_date.day, unloading_date.hour, unloading_date.minute, unloading_date.second)
            unloading_date = temp
            Flag = True

        if loading_date.year>today.year:
            temp = datetime(today.year, loading_date.month, loading_date.day, loading_date.hour, loading_date.minute, loading_date.second)
            if delivery_date<=today and delivery_date.month>loading_date.month:
                temp = datetime(delivery_date.year, loading_date.month, loading_date.day, loading_date.hour, loading_date.minute, loading_date.second)
            loading_date = temp
            flag = True

        entry['LoadingDate'] = str(date(loading_date.year, loading_date.month, loading_date.day))
        entry['UnloadingDate'] = str(date(unloading_date.year, unloading_date.month, unloading_date.day))
        entry['DeliveryDate'] = str(date(delivery_date.year, delivery_date.month, delivery_date.day))
    if flag==False: 
        print("No Changes made when replacing loading and unloading outliers....")
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
    elif (means_of_transport=='sea') or ('container' in means_of_transport):
        return 50
    elif means_of_transport=='truck':
        return 5
    elif means_of_transport in ['courier','express']:
        return 2
    return 2

def fix_unload_before_load(data):
    print("\n")
    flag = False
    for entry in tqdm(data, desc="Fixing Unloads before Loads"):

        transport = entry['MeansOfTransport']
        loading_date_as_string = str(entry['LoadingDate'])
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d") #T%H:%M:%S
        unloading_date_as_string = str(entry['UnloadingDate'])
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d") #T%H:%M:%S
        
        if unloading_date<loading_date:
            unloading_date = loading_date+timedelta(get_transport_ETA(transport.lower()))
            flag = True

        entry['LoadingDate'] = str(date(loading_date.year, loading_date.month, loading_date.day))
        entry['UnloadingDate'] = str(date(unloading_date.year, unloading_date.month, unloading_date.day))
    if flag==False: 
        print("No Changes made while fixing unloading before loading....")
    return data

def fix_deliv_before_unload(data):
    print("\n")
    flag = False
    for entry in tqdm(data, desc="Fixing Delivery before Unloading"):
        
        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")
        unloading_date_as_string = str(entry['UnloadingDate'])
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d") #T%H:%M:%S

        if delivery_date<unloading_date:
            temp = unloading_date+timedelta(median_delivery)
            delivery_date = temp
            flag = True
        entry['DeliveryDate'] = str(date(delivery_date.year, delivery_date.month, delivery_date.day))
    if flag==False: 
        print("No Changes made while fixing delivery before unloading....")
    return data

def print_date_flags(data, tag=''):
    unload_lessthan_load = 0
    deliv_lessthan_unload = 0
    deliv_lessthan_load = 0
    for entry in data:
        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")
        loading_date_as_string = str(entry['LoadingDate'])
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d") #T%H:%M:%S
        unloading_date_as_string = str(entry['UnloadingDate'])
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d") #T%H:%M:%S
        if unloading_date<loading_date:
            unload_lessthan_load = unload_lessthan_load+1
        if delivery_date<unloading_date:
            deliv_lessthan_unload = deliv_lessthan_unload+1
        if delivery_date<loading_date:
            deliv_lessthan_load = deliv_lessthan_load+1
    print(tag, "\nUnload before Load : ",unload_lessthan_load)
    print("Delivery before Unload : ",deliv_lessthan_unload)
    print("Delivery before Load : ",deliv_lessthan_load,'\n')

def drop_invalid_dates_after_correction(data):
    new_data = []
    for entry in tqdm(data, desc="Dropping Uncorrectible Date Entries"):
        loading_date_as_string = str(entry['LoadingDate']).split('T')[0]
        loading_date = datetime.strptime(loading_date_as_string, "%Y-%m-%d")
        
        unloading_date_as_string = str(entry['UnloadingDate']).split('T')[0]
        unloading_date = datetime.strptime(unloading_date_as_string, "%Y-%m-%d")

        delivery_date_as_string = str(entry['DeliveryDate'])
        delivery_date = datetime.strptime(delivery_date_as_string, "%Y-%m-%d")

        if (unloading_date.year>=loading_date.year) and (delivery_date.year>=unloading_date.year):
            new_data.append(entry)
    dropped_count = (len(data)-len(new_data))
    print(dropped_count," entries have been dropped from data due to date issues\n")
    return new_data

def run_date_corrector(data, write:bool = False, targetFilePath:str = '.\Dataset\Dataset_1.json'):
    print("Begin Date Corrections")
    get_max_min_dates(data)
    print_years(data,"(Before Processing)")
    data = correct_year(data)
    print_years(data,"(After First typo correction)")
    data = correct_year_typing_typos(data)
    print_years(data,"(After Second correction)")
    data = correct_year_anomalies(data)
    print_years(data,"(After anomaly clearance)")
    print_year_combos(data,"(Before combination processing)")
    data = correct_unload_load_switch(data)
    print_year_combos(data,"(After clearing loading-unloading date switch)")
    data = correct_unload_delivery_switch(data)
    print_year_combos(data,"(After clearing unloading-delivery date switch)")
    data = replace_loading_unloading_outlier(data)
    data = fix_unload_before_load(data)
    data = fix_deliv_before_unload(data)
    print_date_flags(data,"After completed corrections : ")
    data = drop_invalid_dates_after_correction(data)
    if write==True:
        with open(targetFilePath, "w") as json_file:
            json.dump(data, json_file, indent=4)
    else:
        return data

# run_date_corrector(True)