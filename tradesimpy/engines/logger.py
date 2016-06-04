import logging as log
from datetime import datetime

def init_logger(log_uri):
	log_uri = log_uri + '/engine_log_' + str(datetime.now()) + ".log"
	log.basicConfig(filename=log_uri, level=log.INFO, datefmt='%Y-%m-%d %H:%M:%S', \
		format='%(asctime)s.%(msecs)d - %(levelname)s - %(module)s.%(funcName)s - %(message)s')
	log.getLogger().addHandler(log.StreamHandler())
