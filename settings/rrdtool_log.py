# call from climaduino top-level directory using
# python -m settings.climaduino-controller

# Used the following for ideas on using coroutines:
# http://www.dabeaz.com/coroutines/index.html
# http://lgiordani.github.io/blog/2013/03/25/python-generators-from-iterators-to-cooperative-multitasking/
try:
	import rrdtool
except ImportError:
	raise Exception("python-rrdtool library is not installed")
import json, time, os

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

def coroutine(func):
	'''Convenience decorator to call the first .next() to 'prime' the
	co-routine

	taken from one of the sources listed at the top of the page'''

	def start(*args,**kwargs):
		cr = func(*args,**kwargs)
		cr.next()
		return cr
	return start

@coroutine
def log_data():
	while 1:
		data = (yield)
		rrd_file = "temp_humidity-%s.rrd" % data["device_id"]
		try:
			rrdtool.update(rrd_file, "N:%f:%f:%f:%f" % (data["readings"]["temp"], data["parameters"]["temp"], data["readings"]["humidity"], data["parameters"]["humidity"]))
		except rrdtool.error as details:
			print(details)
			print("Database probably does not exist. Attempting to create it.")
			create_database(file_name=rrd_file)
		except KeyError as details:
			print("%s data was missing. Skipped." % details)

@coroutine
def display_data():
	import pprint
	while 1:
		data = (yield)
		pprint.pprint(data)
		# try:
		# 	for key in data:
		# 		print("---- %s ----" % key)
		# 		message = []
		# 		for item in data[key]:
		# 			message.append("%s: %s" % (item, data[key][item]))
		# 		print(", ".join(message))
		# except:
		# 	pass

@coroutine
def broadcast(targets):
	while 1:
		data = (yield)
		for target in targets:
			target.send(data)

def main(queue, interval_in_seconds):
	import Queue
	# set process niceness value to lower its priority
	os.nice(1)

	# comment the line below and uncomment the line below it if you want the data logged to screen
	data_logger = broadcast([log_data()]) #broadcast data to logger
	#data_logger = broadcast([log_data(), display_data()]) #broadcast data to logger and print to screen

	# We are going to create a loop that looks for a line on Serial. If there is a line,
	# send it to the co-routine that interprets and logs it.
	#
	# If there is a message to send on Serial, it picks it up, and sends it.
	print("rrdtool logger started")
	while 1:
		items_available = True
		data_item={}
		while items_available:
			try:
				item = queue.get(False) #non-blocking read
			except Queue.Empty:
				items_available = False
			else:
				data_item.update(item)
		if len(data_item)>0:
			data_logger.send(data_item)
		time.sleep(interval_in_seconds)

# if called directly from the command line, then execute the main() function
if __name__ == "__main__":
	main()
