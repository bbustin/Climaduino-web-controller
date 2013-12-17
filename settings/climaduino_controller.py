# call from climaduino top-level directory using
# python -m settings.climaduino-controller

# Used the following for ideas on using coroutines:
# http://www.dabeaz.com/coroutines/index.html
# http://lgiordani.github.io/blog/2013/03/25/python-generators-from-iterators-to-cooperative-multitasking/
try:
	import serial
except:
	raise Exception("pySerial library is not installed")
try:
	import rrdtool
except:
	raise Exception("python-rrdtool library is not installed")
import json, time

## Django stuff
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'climaduino.settings'
from models import Setting, Reading
from django.utils import timezone
##

rrd_file = "temp_humidity-2.rrd"

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
		try:
			rrdtool.update(rrd_file, "N:%f:%f:%f:%f" % (data["readings"]["temp"], data["parameters"]["temp"], data["readings"]["humidity"], data["parameters"]["humidity"]))
		except (KeyError, rrdtool.error) as details:
			print(details)

@coroutine
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

@coroutine
def update_database():
	last_data = {'readings':{'temp':0,'humidity':0}, 'parameters':None}
	while 1:
		update_time = timezone.now()
		data = (yield)
		# Round current temperature and humidity readings
		temperature_rounded = round(data["readings"]["temp"])
		humidity_rounded = round(data["readings"]["humidity"])

		# Compare rounded current readings against the rounded previous readings
		if (round(last_data["readings"]["temp"]) != temperature_rounded) or (round(last_data["readings"]["humidity"]) != humidity_rounded):
			try:
				reading_record = Reading.objects.get(pk=1)
			except Reading.DoesNotExist:
				reading_record = Reading(time=update_time, temperature=temperature_rounded, humidity=humidity_rounded)
			else:
				reading_record.time = update_time
				reading_record.temperature = temperature_rounded
				reading_record.humidity = humidity_rounded
			reading_record.save()
		if last_data["parameters"] != data["parameters"]:
			setting_record = Setting(time=update_time, source=0, mode=data["parameters"]["mode"], temperature=data["parameters"]["temp"], humidity=data["parameters"]["humidity"])
			setting_record.save()
		last_data = data

@coroutine
def unserialize_data(target):
	while 1:
		try:
			serial_data = (yield)
			data = json.loads(serial_data)
		except ValueError:
			pass
		else: 
			target.send(data)

@coroutine
def broadcast(targets):
	while 1:
		data = (yield)
		for target in targets:
			target.send(data)

def main(queue):
	import Queue
	# set process niceness value to lower its priority
	os.nice(1)
	try:
	  with open(rrd_file):
	   	print("Database Exists")
	except IOError:
	  print("Creating Database...")
	  create_database()

	try:
		serial_port = serial.Serial("/dev/ttyACM0", 9600, timeout=0) #open in non-blocking mode
	except serial.SerialException, e:
		raise e
	else:
		print("Climaduino controller using serial port: %s" % serial_port.name)

		unserialize = unserialize_data(broadcast([log_data(), update_database()])) #instantiate unserialize coroutine and broadcast result to logger and update_database
		# comment out the previous line and uncomment the next line if you would like text output of the current readings from the controller
		#unserialize = unserialize_data(broadcast([log_data(), update_database(), display_data()])) #instantiate unserialize coroutine and broadcast result to logger and update_database

		# We are going to create a loop that looks for a line on Serial. If there is a line,
		# send it to the co-routine that interprets and logs it.
		#
		# If there is a message to send on Serial, it picks it up, and sends it.
		last_serial_read = None
		while 1:
			if last_serial_read == None or (time.time() - last_serial_read > 4): # only check Serial port at most every 4 seconds
				line = serial_port.readline()
				last_serial_read = time.time()
				if line:
					unserialize.send(line)
			try:
				parameter = queue.get(False) #non-blocking read. If empty, we handle the exception below
			except Queue.Empty:
				pass
			else:
				print(parameter)
				serial_port.write(str(parameter))
			time.sleep(.25)
	finally:
		serial_port.close()

# if called directly from the command line, then execute the main() function
if __name__ == "__main__":
	main()
