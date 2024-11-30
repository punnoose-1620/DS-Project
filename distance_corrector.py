import json
from tqdm import tqdm

categories = []
distance_values = {}

from_country_key = 'FromISO'
to_country_key = 'ToISO'
distance_key = 'Distance'

data_file = '.\Dataset\Dataset_1.json'
target_data_file = '.\Dataset\Dataset_2.json'

def categorise_entries(data):
    # print('\n')
    countries_logged = []
    for entry in tqdm(data, desc="Finding Categories"):
        from_country = str(entry[from_country_key])
        to_country = str(entry[to_country_key])
        if [from_country, to_country] not in categories:
            categories.append([from_country, to_country])
        if from_country not in countries_logged:
            countries_logged.append(from_country)
        if to_country not in countries_logged:
            countries_logged.append(to_country)
    print(len(countries_logged),' countries have been logged')
    print(len(categories),' shipping combinations found')

def get_distance_values(data):
    # print('\n')
    for entry in tqdm(data, desc="Getting Distance Sum and Count for mean"):
        ref_keys = distance_values.keys()
        from_country = str(entry[from_country_key]).strip()
        to_country = str(entry[to_country_key]).strip()
        distance_as_string = str(entry[distance_key]).strip().lower()
        if len(distance_as_string)!=0 and distance_as_string!='null' and distance_as_string!='none':
            distance = float(distance_as_string)
            item_key = from_country+'_'+to_country
            value = {
                    'sum': distance,
                    'count': 1
                }
            if item_key in ref_keys:
                value = distance_values[item_key]
                value['sum'] = value['sum']+distance
                value['count'] = value['count']+1
            distance_values[item_key] = value
    print(len(distance_values.keys()),' distances have been found')

def get_means():
    print('\n')
    ref_keys = distance_values.keys()
    for key in tqdm(ref_keys, desc="Getting mean distances"):
        distance_values[key]['mean'] = distance_values[key]['sum']/distance_values[key]['count']
        # distance_values[key] = distance_values[key]

def print_means():
    print('\n')
    ref_keys = distance_values.keys()
    for key in ref_keys:
        endpoints = key.split('_')
        print(endpoints[0],' to ',endpoints[1],' : ',json.dumps(distance_values[key], indent=4))

def replace_empty_values(data):
    # print('\n')
    replace_count = 0
    for entry in tqdm(data, desc='Replacing Empty/null values for distance'):
        distance_as_string = str(entry[distance_key]).strip().lower()
        from_country = str(entry[from_country_key])
        to_country = str(entry[to_country_key])
        if len(distance_as_string)==0 or distance_as_string=='null' or distance_as_string=='none':
            ref_key = from_country+'_'+to_country
            if ref_key in distance_values.keys():
                values = distance_values[ref_key]
                distance_as_string = values['mean']
                replace_count = replace_count+1
        if distance_as_string!='null' and distance_as_string!='none':
            entry[distance_key] = float(distance_as_string)
    print(replace_count,' values replaced with mean')
    return data

def print_non_numeric_distances(data):
    entry_types = {}
    for entry in data:
        ref_keys = entry_types.keys()
        distance_as_string = str(entry[distance_key]).strip().lower()
        try:
            distance = float(distance_as_string)
        except:
        # if type(entry[distance_key]) is not int or type(entry[distance_key]) is not float:
            if len(distance_as_string)==0:
                distance_as_string = 'empty'
            if distance_as_string not in ref_keys:
                entry_types[distance_as_string] = 1
            else:
                entry_types[distance_as_string] = entry_types[distance_as_string]+1
    print(len(entry_types.keys()),' non-numeric distances found')
    if len(entry_types.keys())>0:
        # print(json.dumps(entry_types, indent=4))
        print(str(entry_types).replace('}','').replace('{',''))

def drop_final_empty_distance_entries(data):
    print('\nData count before drop : ',len(data))
    new_data = []
    for entry in tqdm(data, desc="Dropping persistant invalid distances after correction"):
        distance_raw = entry[distance_key]
        if type(distance_raw) in (int, float):
            new_data.append(entry)
    print('Data count before drop : ',len(new_data))
    print('Drop Count : ',str(len(data)-len(new_data)))
    return new_data

def run_distance_corrector():
    with open(data_file, 'r') as file:
        data = json.load(file)
        print_non_numeric_distances(data)
        categorise_entries(data)
        get_distance_values(data)
        get_means()
        # print_means()
        data = replace_empty_values(data)
        print_non_numeric_distances(data)
        data = drop_final_empty_distance_entries(data)
        print_non_numeric_distances(data)
        with open(target_data_file, "w") as json_file:
            json.dump(data, json_file, indent=4)

run_distance_corrector()