import pandas as pd
import pandas.io.sql as pd_sql
from pandas import DataFrame

import numpy as np

import matplotlib.pyplot as plt
from sklearn import preprocessing

# csv파일 열기
df = pd.read_csv("../data/NODE_RAW_1215_ET_1.csv", parse_dates=[2,3])

df = DataFrame(df, columns=['AMPERE','VOLTAGE'])
df = preprocessing.scale(df)

print(df)

#df = DataFrame(df)


#df.rename(columns = {'NODE_ID' : 'node_id'}, inplace = True)
#df.rename(columns = {'EVENT_TIME' : 'times'}, inplace = True)
#df.rename(columns = {'VOLTAGE' : 'voltage'}, inplace = True)

#plt.plot(df.times, df.voltage)	#그래프화 (x,y)
#plt.plot(df.times, df.voltage, linestyle='-', marker='o', label="value")
#plt.show()	#그래프 출력

#df = df.T 	#행렬 전치(transpose)

#print(df.times[0:10])	#출력범위
#print(df.columns.tolist()) #컬럼 데이터타입 확인
#data_list = df.values.tolist() #데이터 리스트화
#df.info()	#데이터 속성정보확인
#df3.to_csv('test.csv', sep=',', encoding='utf-8') #데이터 저장

#print(df)
#print(df.axes)

#print(df.pivot_table(index='EVENT_TIME', columns='NODE_ID', values='VOLTAGE', aggfunc='first'))
#df1 = df.pivot_table(index=['EVENT_TIME'], columns='NODE_ID', values=['ACTIVE_POWER', 'POWER_FACTOR'])
#df2 = df1.resample('15T').mean()
#df2 = df1.groupby(df1.TimeGroup(freq='10Min')).aggregate(numpy.sum)
#df3 = df2.T
#print(df3)

#df2 = df1.T
#print(df2)

#print(df)
