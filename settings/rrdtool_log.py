# call from climaduino top-level directory using
# python -m settings.climaduino-controller

# Used the following for ideas on using coroutines:
# http://www.dabeaz.com/coroutines/index.html
# http://lgiordani.github.io/blog/2013/03/25/python-generators-from-iterators-to-cooperative-multitasking/
try:
	import rrdtool
except ImportError:
	raise ImportError("python-rrdtool library is not installed")
import json, time

def create_database(file_name=rrd_file, interval_in_seconds="60"): 
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

def log_data(rrd_file, temperature, humidity):
	try:
		rrdtool.update(rrd_file, "N:%f:%f:%f:%f" % (temperature, None, humidity, None))
	except (KeyError, rrdtool.error) as details:
		print(details)

def display_data():
	while 1:
		data = (yield)
		try:
			for key in data:
				print("---- %s ----" % key)
				message = []
				for item in data[key]:
					message.append("%s: %s" % (item, data[key][item]))
				print(", ".join(message))
		except:
			pass

def broadcast(targets):
	while 1:
		data = (yield)
		for target in targets:
			target.send(data)

def main(device_id, temperature, humidity):
	rrd_file = "temp_humidity-%s" % device_id
	try:
	  with open(rrd_file):
	   	print("Database Exists")
	except IOError:
	  print("Creating Database...")
	  create_database()
	log_data(rrd_file, temperature, humidity)

# if called directly from the command line, then execute the main() function
if __name__ == "__main__":
	main()
