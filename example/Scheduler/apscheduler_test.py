#from apscheduler.schedulers.blocking import BlockingScheduler
#from apscheduler.schedulers.background import BackgroundScheduler
import socket
import time

import daemon

import logging
import logging.handlers

import configparser

# 전역변수로 처리 필요
config = configparser.ConfigParser()
config.read('../config.cfg')
cfg_server = config['SERVER_INFO']
cfg_default = config['DEFAULT_INFO']

def job_cron_day():
	HOST = 'DataAnalyzer'
	PORT = 5225
	print("Start data analysis")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #소켓생성
	s.connect((HOST,PORT))
	s.send(b'{"start_date": "2017-02-03", "end_date": "2017-02-03", "time_interval": 60}') #문자를 보냄
	data = s.recv(2048) #서버로 부터 정보를 받음
	s.close()
	print('Received',repr(data))

def job_cron_week():
	HOST = 'DataAnalyzer'
	PORT = 5225
	print("Start data analysis")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #소켓생성
	s.connect((HOST,PORT))
	s.send(b'{"start_date": "2017-02-07", "end_date": "2017-02-07", "time_interval": 30}') #문자를 보냄
	data = s.recv(2048) #서버로 부터 정보를 받음
	s.close()
	print('Received',repr(data))

def run():
	from apscheduler.schedulers.blocking import BlockingScheduler
	print("test")
	sched = BlockingScheduler(timezone='KST')
	#sched = BackgroundScheduler()
	#sched.daemonic = False
	# Schedules job_function to be run on the third Friday
	# of June, July, August, November and December at 00:00, 01:00, 02:00 and 03:00
	sched.add_job(job_cron_day, 'cron', max_instances=10, day_of_week='mon-fri', second='*/30')
	sched.add_job(job_cron_week, 'cron', max_instances=10, day_of_week='mon-fri', minute='*/50')
	#sched.add_job(job_function, 'cron', day_of_week='fri-sun', hour=1)
	try:
		sched.start()
	except Exception as e:
		print("Got SIGTERM! Terminating...")
		sched.shutdown(wait=False)


def start_daemon():
	# make logger instance
	logger = logging.getLogger("APS_daemonLog")
	logger.setLevel(logging.INFO)

	# make formatter
	formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')

	# make handler to output Log for stream and file
	fileMaxByte = 1024 * 1024 * 100 #100MB
	fileHandler = logging.handlers.RotatingFileHandler(cfg_default['apscheduler_path'], maxBytes=fileMaxByte, backupCount=10)

	# fileHandler = logging.FileHandler(cfg_default['logging_path'])
	streamHandler = logging.StreamHandler()

	# specify formatter to each handler
	fileHandler.setFormatter(formatter)
	streamHandler.setFormatter(formatter)

	# attach stream and file handler to logger instance
	logger.addHandler(fileHandler)
	logger.addHandler(streamHandler)


	daemon_context = daemon.DaemonContext()

	print("Start daemon for EyeLink in python")

	with daemon_context:
		while True:
			logger.info("==========================")
			logger.debug("Debug message")
			logger.info("Info message")
			logger.warn("Warning message")
			logger.error("Error message")
			logger.critical("critical debug message")
			logger.info("==========================")

			run()

if __name__ == '__main__':
	start_daemon()
	#run()