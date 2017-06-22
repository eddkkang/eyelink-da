## main module for analysis of time series clustering ##
# coding: utf-8
from pprint import pprint
# default lib
import json
from collections import OrderedDict
import datetime
import logging
import logging.handlers

##### required library #####
import pandas as pd
import requests

# ## required eyelink modules ##
import config_info as config
import elda_data_extraction as elda_de
import elda_ts_clustering_test as elda_tsc

#load_url = "http://m2utech.eastus.cloudapp.azure.com:5223/dashboard/restapi/getTbRawDataByPeriod"
load_url = config.cfg['data_load_url']

################ Logging ##################
# make logger instance
logger = logging.getLogger("Running_Log")
#########################################


def data_load(s_date, e_date, t_iterval):
	start_date = s_date
	end_date = e_date
	time_interval = t_iterval
	#nowtime = datetime.datetime.now()
	nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

	##### JSON 로드 #####
	'''
	url = load_url + "?startDate={}&endDate={}".format(start_date, end_date)
	resp = requests.get(url)
	dataset = json.loads(resp.text)
	'''

	json_data = open('./testdata.json').read()
	dataset = json.loads(json_data)

	####### create test dataset #######
	"""
	data = json.dumps(dataset)
	f = open("testdata.json","w")
	f.write(data)
	f.close()
	"""
	#########################################

	if not dataset['rtnData']:
		print("empty dataset")

	else:
		##### 분석할 데이터 속성 추출 #####
		dataset = pd.DataFrame(dataset['rtnData'], columns=['node_id', 'event_time', 'voltage', 'ampere', 'active_power', 'power_factor'])

		logger.info("Data Analysis start... >> data size : {} rows".format(len(dataset.index)))
		
		##### 데이터 타입 변환 #####
		dataset['voltage'] = dataset['voltage'].apply(pd.to_numeric, errors='ignore')
		dataset['ampere'] = dataset['ampere'].apply(pd.to_numeric, errors='ignore')
		dataset['active_power'] = dataset['active_power'].apply(pd.to_numeric, errors='ignore')
		dataset['power_factor'] = dataset['power_factor'].apply(pd.to_numeric, errors='ignore')
		dataset['event_time'] = pd.to_datetime(dataset['event_time'], format='%Y-%m-%d %H:%M:%S.%f')


		################## 피벗 및 클러스터링 ####################
		# function (data, index, columns, values, default_value) #
		voltage_data = elda_de.extract_data(dataset, 'event_time', 'node_id', 'voltage', 200, time_interval)
		ampere_data = elda_de.extract_data(dataset, 'event_time', 'node_id', 'ampere', 0.5, time_interval)
		active_power_data = elda_de.extract_data(dataset, 'event_time', 'node_id', 'active_power', 170, time_interval)
		power_factor_data = elda_de.extract_data(dataset, 'event_time', 'node_id', 'power_factor', 0.9, time_interval)

		###### 결과 테이블 ######
		result_tb = pd.DataFrame()
		result_tb['event_time'] = voltage_data.index
		result_tb['da_time'] = nowtime
		result_tb = result_tb[['da_time','event_time']]

		master_tb = pd.DataFrame(index=[0])
		master_tb['da_time'] = nowtime
		master_tb['start_date'] = start_date
		master_tb['end_date'] = end_date
		master_tb['time_interval'] = time_interval

		###### time-series format ######
		v_ts = {}
		a_ts = {}
		ap_ts = {}
		pf_ts = {}
		
		for i in range(len(voltage_data.columns)):
			v_ts[voltage_data.columns[i]] = voltage_data.ix[:,i]
			a_ts[ampere_data.columns[i]] = ampere_data.ix[:,i]
			ap_ts[active_power_data.columns[i]] = active_power_data.ix[:,i]
			pf_ts[power_factor_data.columns[i]] = power_factor_data.ix[:,i]

		##### column list #####
		v_col_list = list(voltage_data.columns)
		a_col_list = list(ampere_data.columns)
		ap_col_list = list(active_power_data.columns)
		pf_col_list = list(power_factor_data.columns)

		##### Convert dict list for clustering analysis
		v_ls = {}
		a_ls = {}
		ap_ls = {}
		pf_ls = {}
		
		for i in range(len(voltage_data.columns)):
			v_ls[str(v_col_list[i])] = v_ts[str(voltage_data.columns[i])].tolist()
			a_ls[str(a_col_list[i])] = a_ts[str(ampere_data.columns[i])].tolist()
			ap_ls[str(ap_col_list[i])] = ap_ts[str(active_power_data.columns[i])].tolist()
			pf_ls[str(pf_col_list[i])] = pf_ts[str(power_factor_data.columns[i])].tolist()

		print(type(pf_ls))
		import pdb; pdb.set_trace()  # breakpoint e6f645d1 //

		############# sort list ###############
		# from collections import OrderedDict #
		v_ls = OrderedDict(sorted(v_ls.items(), key=lambda x:x[1], reverse=True))
		a_ls = OrderedDict(sorted(a_ls.items(), key=lambda x:x[1], reverse=True))
		ap_ls = OrderedDict(sorted(ap_ls.items(), key=lambda x:x[1], reverse=True))
		pf_ls = OrderedDict(sorted(pf_ls.items(), key=lambda x:x[1], reverse=True))

#		f = open('testdata.txt', 'w')
#		f.write(str(pf_ls))

		print(pf_ls.items())
		print(type(pf_ls))
		import pdb; pdb.set_trace()  # breakpoint 0926e0f2 //

		"""
		#################### clustering ###################

		##### voltage #####
		v_centroids, v_assignments = elda_tsc.k_means_clust(v_ls,4,2,2) #data, clus_num, iter, window
		## datail result ##
		print("***************")
		print(v_centroids)
		print("***************")
		v_result_centroids = pd.DataFrame(v_centroids)
		v_result_centroids.reset_index(level=0, inplace=True)
		v_result_centroids = v_result_centroids.pivot_table(columns = 'index')
		result_tb['c0_voltage'] = v_result_centroids.loc[:,0]
		result_tb['c1_voltage'] = v_result_centroids.loc[:,1]
		result_tb['c2_voltage'] = v_result_centroids.loc[:,2]
		result_tb['c3_voltage'] = v_result_centroids.loc[:,3]


		## master result ##
		v_assign = ",".join(map(str, list(v_assignments.values())))
		v_assign = v_assign.replace(", ",":").replace("'","").replace("[","").replace("]","")
		v_assign = v_assign.split(',')
		v_assign = pd.DataFrame(v_assign).T
		master_tb['c0_voltage'] = v_assign.loc[:,0]
		master_tb['c1_voltage'] = v_assign.loc[:,1]
		master_tb['c2_voltage'] = v_assign.loc[:,2]
		master_tb['c3_voltage'] = v_assign.loc[:,3]


		##### ampere #####
		a_centroids, a_assignments = elda_tsc.k_means_clust(a_ls,4,2,2)
		## datail result ##
		print("***************")
		print(a_centroids)
		print("***************")
		a_result_centroids = pd.DataFrame(a_centroids)
		a_result_centroids.reset_index(level=0, inplace=True)
		a_result_centroids = a_result_centroids.pivot_table(columns = 'index')
		result_tb['c0_ampere'] = a_result_centroids.loc[:,0]
		result_tb['c1_ampere'] = a_result_centroids.loc[:,1]
		result_tb['c2_ampere'] = a_result_centroids.loc[:,2]
		result_tb['c3_ampere'] = a_result_centroids.loc[:,3]
		## master result ##
		a_assign = ",".join(map(str, list(a_assignments.values())))
		a_assign = a_assign.replace(", ",":").replace("'","").replace("[","").replace("]","")
		a_assign = a_assign.split(',')
		a_assign = pd.DataFrame(a_assign).T
		master_tb['c0_ampere'] = a_assign.loc[:,0]
		master_tb['c1_ampere'] = a_assign.loc[:,1]
		master_tb['c2_ampere'] = a_assign.loc[:,2]
		master_tb['c3_ampere'] = a_assign.loc[:,3]


		##### active power #####
		ap_centroids, ap_assignments = elda_tsc.k_means_clust(ap_ls,4,2,2)
		## detail result ##
		print("***************")
		print(ap_centroids)
		print("***************")
		ap_result_centroids = pd.DataFrame(ap_centroids)
		ap_result_centroids.reset_index(level=0, inplace=True)
		ap_result_centroids = ap_result_centroids.pivot_table(columns = 'index')
		result_tb['c0_active_power'] = ap_result_centroids.loc[:,0]
		result_tb['c1_active_power'] = ap_result_centroids.loc[:,1]
		result_tb['c2_active_power'] = ap_result_centroids.loc[:,2]
		result_tb['c3_active_power'] = ap_result_centroids.loc[:,3]
		## master result ##
		ap_assign = ",".join(map(str, list(ap_assignments.values())))
		ap_assign = ap_assign.replace(", ",":").replace("'","").replace("[","").replace("]","")
		ap_assign = ap_assign.split(',')
		ap_assign = pd.DataFrame(ap_assign).T
		master_tb['c0_active_power'] = ap_assign.loc[:,0]
		master_tb['c1_active_power'] = ap_assign.loc[:,1]
		master_tb['c2_active_power'] = ap_assign.loc[:,2]
		master_tb['c3_active_power'] = ap_assign.loc[:,3]
		"""

		##### power factor #####
		pf_centroids, pf_assignments = elda_tsc.k_means_clust(pf_ls,4,2,5)
		## detail result ##
		print("***************")
		print(pf_centroids)
		print("***************")
		pf_result_centroids = pd.DataFrame(pf_centroids)
		print(pf_result_centroids)
		pf_result_centroids.reset_index(level=0, inplace=True)
		

		pf_result_centroids = pf_result_centroids.pivot_table(columns = 'index')
		result_tb['c0_power_factor'] = pf_result_centroids.loc[:,0]
		result_tb['c1_power_factor'] = pf_result_centroids.loc[:,1]
		result_tb['c2_power_factor'] = pf_result_centroids.loc[:,2]
		result_tb['c3_power_factor'] = pf_result_centroids.loc[:,3]
		## master result ##
		pf_assign = ",".join(map(str, list(pf_assignments.values())))
		pf_assign = pf_assign.replace(", ",":").replace("'","").replace("[","").replace("]","")
		pf_assign = pf_assign.split(',')
		pf_assign = pd.DataFrame(pf_assign).T
		master_tb['c0_power_factor'] = pf_assign.loc[:,0]
		master_tb['c1_power_factor'] = pf_assign.loc[:,1]
		master_tb['c2_power_factor'] = pf_assign.loc[:,2]
		master_tb['c3_power_factor'] = pf_assign.loc[:,3]


		import pdb; pdb.set_trace()  # breakpoint 09289591 //

		### Merge JSON in dictionary type for converting timestamp data ####
		result_json = {}
		result_json['tb_da_clustering_master'] = master_tb.to_dict(orient='records')
		result_json['tb_da_clustering_detail'] = result_tb.to_dict(orient='records')

		### timestamp convert ###
		def myconverter(o):
			if isinstance(o, datetime.datetime):
				return o.__str__()

		result_json = json.dumps(result_json, default = myconverter, sort_keys=True)
		result_json = json.loads(result_json)

	#	print(result_json)

		#upload_url = "http://192.168.10.64:5223/analysis/restapi/insertClusterRawData"
		#upload_url = "http://m2utech.eastus.cloudapp.azure.com:5223/analysis/restapi/insertClusterRawData"
		upload_url = config.cfg['result_upload_url']
		#print(upload_url)

		r = requests.post(upload_url, json=result_json)

		print("no problem!!!!!!!!!!!!!!!")

####################################
if __name__ == '__main__':
	#pass
	data_load('2017-02-07', '2017-02-07', 30)
	# data_load(config.cfg['s_date'], config.cfg['e_date'], int(config.cfg['t_interval']))