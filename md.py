#!/usr/bin/env python
#-*- coding: 'utf-8' -*-
import csv
import glob
import os
import datetime
import pytz
import json
import pandas as pd

#Program Configuration-------------------
import config
DIR_DATA=config.DIR_DATA
LIST_SOURCES=config.LIST_SOURCES
SPATIAL_THRESHOLD=config.SPATIAL_THRESHOLD
DIR_DATAANALYSIS=config.DIR_DATAANALYSIS
DIR_HEALTH_LOG=config.DIR_HEALTH_LOG
#########################################
current=datetime.datetime.now(pytz.timezone('Asia/Taipei'))
today=current.date()
yesterday=today-datetime.timedelta(1)
date=yesterday.strftime('%Y%m')
day=yesterday.strftime('%d')
feeds=[]
ind_feeds=[]
emi_feeds=[]
for source in LIST_SOURCES:
	src_directory=DIR_DATA+source
	health_src_directory=DIR_HEALTH_LOG+source
	for device_directory in glob.glob(src_directory+'/*'):
		csv_path=device_directory+'/'+date+'.csv'
		if os.path.exists(csv_path):
			df=pd.read_csv(csv_path,delimiter=' ',header=None,dtype={0:object})
			df[0]=df[0].astype(str)
			df=df[df[0].str.startswith(day)]
			if df.shape[0]!=0:
				df[4]=df[2].apply(config.get_pm_level)
				df[4]=df[4].replace(SPATIAL_THRESHOLD)
				df=df[df[1]>=0]
				indoor_df=df[df[2]-df[1]>df[4]]
				indoor_df=indoor_df[indoor_df[3]>=2]
				emission_df=df[df[1]-df[2]>df[4]]
				emission_df=emission_df[emission_df[3]>=2]
				emission_df=emission_df[emission_df[1]>30.0]
				nocomment_df=df[df[3]<2]
				splitted=csv_path.split('/')
				indoor=indoor_df.shape[0]/float(df.shape[0])
				emission=emission_df.shape[0]/float(df.shape[0])
				nocomment=nocomment_df.shape[0]/float(df.shape[0])
				temp = {'device_id':splitted[-2],'1':nocomment,'2':emission,'3':indoor}
				feeds.append(temp)
				compare=[indoor,emission,nocomment]
				if compare.index(max(compare))==0 and indoor>=1.0/3.0:
					temp = {'device_id':splitted[-2],'rate':indoor}
					ind_feeds.append(temp)
				if compare.index(max(compare))==1 and emission>=1.0/3.0:
					temp = {'device_id':splitted[-2],'rate':emission}
					emi_feeds.append(temp)
				health_csv=health_src_directory+'/'+splitted[-2]+'.csv'
				if not os.path.exists(health_csv):
					with open(health_csv,'w') as f:pass
				mycsv=open(health_csv,'a')
				row=date+day+' '+str(nocomment)+' '+str(emission)+' '+str(indoor)+'\n'
				mycsv.write(row)
				mycsv.close()

msg = {}
msg["source"] = str("device_malfunction_daily by IIS-NRL").encode("utf-8")
msg["feeds"] = feeds
msg["description-type"]={"type-1":"non-detectable","type-2":"spatially greater","type-3":"spatially less"}
utc_datetime = datetime.datetime.utcnow()
msg["version"] = utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
with open(DIR_DATAANALYSIS+'device_malfunction_daily.json','w') as fout:
	json.dump(msg,fout)

# msg = {}
# msg["source"] = str("device_indoor by IIS-NRL").encode("utf-8")
# msg["feeds"] = ind_feeds
# utc_datetime = datetime.datetime.utcnow()
# msg["version"] = utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
# with open(DIR_DATAANALYSIS+'device_indoor.json','w') as fout:
# 	json.dump(msg,fout)

msg = {}
msg["source"] = str("device_indoor by IIS-NRL").encode("utf-8")
msg["feeds"] = ind_feeds
utc_datetime = datetime.datetime.utcnow()
msg["version"] = utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
with open(DIR_DATAANALYSIS+'device_indoor_1.json','w') as fout:
	json.dump(msg,fout)

# msg = {}
# msg["source"] = str("device_emission by IIS-NRL").encode("utf-8")
# msg["feeds"] = emi_feeds
# utc_datetime = datetime.datetime.utcnow()
# msg["version"] = utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
# with open(DIR_DATAANALYSIS+'device_emission.json','w') as fout:
# 	json.dump(msg,fout)

msg = {}
msg["source"] = str("device_emission by IIS-NRL").encode("utf-8")
msg["feeds"] = emi_feeds
utc_datetime = datetime.datetime.utcnow()
msg["version"] = utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
with open(DIR_DATAANALYSIS+'device_emission_1.json','w') as fout:
	json.dump(msg,fout)
