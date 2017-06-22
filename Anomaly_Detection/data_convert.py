import numpy as np
import struct
import matplotlib.pyplot as plt
import csv
import datetime
import requests
import json

# configuration
import config_parser as configuration
import pandas as pd

cfg = configuration.cfg_parser()

load_url = cfg.load_url


def json_data_load(node_id, s_date, e_date):
    
    #nowtime = datetime.datetime.now()
    nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    ##### load JSON #####
    url = load_url + "?nodeId={}&startDate={}&endDate={}".format(node_id, s_date, e_date)
    #print(url)

    resp = requests.get(url)
    dataset = json.loads(resp.text)
    #print(dataset)

    if not dataset['rtnData']:
        print("There is no dataset")
        #logger.warning("There is no dataset")

    else:
        dataset = pd.DataFrame(dataset['rtnData'], columns=['node_id', 'event_time', 'voltage'])
        dataset['event_time'] = pd.to_datetime(dataset['event_time'], format='%Y-%m-%d %H:%M:%S.%f')
        dataset['voltage'] = dataset['voltage'].apply(pd.to_numeric, errors='ignore')
        dataset = dataset.set_index('event_time')  

    
    return dataset


def resample_missingValue(dataset, def_val, t_interval):
    # 처음-끝 일정사이에 15분 단위로 구분(비어있는 날짜는 자동으로 생성)
    dataset = dataset.resample(str(t_interval)+'T').mean()
    dataset = dataset.fillna(def_val)

    #dataset = dataset[dataset.voltage != 100]

    return dataset




###############################################
def read_test_data(input_file):
    with open(input_file, 'rb') as input_file:
        data_raw = input_file.readlines()
        
    # sklearn seems to throw up if data not in float format
    # sklearn seems to throw up if data not in float format
    data = np.array(data_raw).astype(float)
    return data

def read_txt_to_numpy(input_file):
    data_raw = np.genfromtxt(input_file, usecols=(0,1), delimiter='\t', dtype=None)
    return data_raw

def read_data(input_file):
    data = np.genfromtxt(input_file, delimiter='\t', dtype=str)
    return data

def plot_test_data(input_file, n_samples):
    """
    Plot the EKG data from the given file (for debugging).
    """
    ekg_data = read_test_data(input_file)
    plt.plot(ekg_data[0:n_samples])
    plt.show()
