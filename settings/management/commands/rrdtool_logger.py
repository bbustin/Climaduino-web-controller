# Used the following for ideas on using coroutines:
# http://www.dabeaz.com/coroutines/index.html
# http://lgiordani.github.io/blog/2013/03/25/python-generators-from-iterators-to-cooperative-multitasking/
import time, os
from django.core.management.base import BaseCommand, CommandError
import json

try:
	import rrdtool
except ImportError:
	print("python-rrdtool library is not installed\nNo logging will be available")

from _common import BridgeServer

data = {}
def socket_handler(self, raw_data):
	json_data = json.loads(raw_data)
	for (device, values) in json_data.items():
		try:
			data[device].update(values)
		except KeyError:
			data[device] = values
	print(data)
	# log_data(data)

def create_database(file_name, interval_in_seconds="60"): 
	error = rrdtool.create(
		file_name, "--step", interval_in_seconds,
		"DS:temperature:GAUGE:30:U:U",
		"DS:temperatureSetPoint:GAUGE:30:U:U",
		"DS:humidity:GAUGE:30:U:U",
		"DS:humiditySetPoint:GAUGE:30:U:U",
		"RRA:AVERAGE:0.2:1:1440", # 1 day of 1-minute accuracy averages
		"RRA:AVERAGE:0.2:5:8640", # 30 days of 5-minute accuracy averages	
		"RRA:AVERAGE:0.2:15:8640", # 90 days 15 minute averages
		"RRA:AVERAGE:0.2:30:8640", # 180 days 30 minute averages
		"RRA:AVERAGE:0.2:60:8760", # 1 year 1 hour averages
		"RRA:AVERAGE:0.2:1440:1460", # 4 years 1 day averages
		"RRA:MAX:0.2:1:1440", # 1 day of 1-minute accuracy maximums
		"RRA:MAX:0.2:5:8640", # 30 days of 5-minute accuracy maximums	
		"RRA:MAX:0.2:15:8640", # 90 days 15 minute maximums
		"RRA:MAX:0.2:30:8640", # 180 days 30 minute maximums
		"RRA:MAX:0.2:60:8760", # 1 year 1 hour maximums
		"RRA:MAX:0.2:1440:1460", # 4 years 1 day maximums
		"RRA:MIN:0.2:1:1440", # 1 day of 1-minute accuracy minimums
		"RRA:MIN:0.2:5:8640", # 30 days of 5-minute accuracy minimums	
		"RRA:MIN:0.2:15:8640", # 90 days 15 minute minimums
		"RRA:MIN:0.2:30:8640", # 180 days 30 minute minimums
		"RRA:MIN:0.2:60:8760", # 1 year 1 hour minimums
		"RRA:MIN:0.2:1440:1460", # 4 years 1 day minimums
		)
	if error:
		raise Exception(rrdtool.error())

def log_data(data):
	print(data)
	for device in data:
		rrd_file = "temp_humidity-%s.rrd" % device
		try:
			rrdtool.update(rrd_file, "N:%f:%f:%f:%f" % (data[device]["readings"]["temperature"], data[device]["settings"]["tempSetPoint"], data[device]["readings"]["humidity"], data[device]["settings"]["humiditySetPoint"]))
		except rrdtool.error as details:
			print(details)
			print("Database probably does not exist. Attempting to create it.")
			create_database(file_name=rrd_file)
		except KeyError as details:
			print("%s data was missing. Skipped." % details)

class Command(BaseCommand):
	args = 'There are no args!'
	help = 'RRDTool logger in charge of logging readings and system setting changes.'

	def handle(self, *args, **options):
		# do not run if rrdtool has not been imported
		try:
			rrdtool
		except NameError:
			return
		import Queue
		# set process niceness value to lower its priority
		os.nice(1)
		bridge_server = BridgeServer()
		bridge_server.socket_start('/tmp/climaduino_rrdtool_logger', socket_handler)
		# keep running indefinitely
		while 1:
			time.sleep(5)

