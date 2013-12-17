# call from climaduino top-level directory using
# python -m settings.climaduino-controller

# Used the following for ideas on using coroutines:
# http://www.dabeaz.com/coroutines/index.html
# http://lgiordani.github.io/blog/2013/03/25/python-generators-from-iterators-to-cooperative-multitasking/
import json, time

## Django stuff
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'climaduino.settings'
from models import Setting, Reading
from django.utils import timezone
##


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
		if (round(last_data["readings"]["temp"]) != round(data["readings"]["temp"])) or (round(last_data["readings"]["humidity"]) != round(data["readings"]["humidity"])):
			try:
				reading_record = Reading.objects.get(pk=1)
			except Reading.DoesNotExist:
				reading_record = Reading(time=update_time, temperature=data["readings"]["temp"], humidity=data["readings"]["humidity"])
			else:
				reading_record.time = update_time
				reading_record.temperature = data["readings"]["temp"]
				reading_record.humidity = data["readings"]["humidity"]
			reading_record.save()
		if last_data["parameters"] != data["parameters"]:
			setting_record = Setting(time=update_time, mode=data["parameters"]["mode"], temperature=data["parameters"]["temp"], humidity=data["parameters"]["humidity"])
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
		pass
	except:
		pass
	else:
		print("Mocking Climaduino reads and writes")
		# We are going to create a loop that looks for a line on Serial. If there is a line,
		# send it to the co-routine that interprets and logs it.
		#
		# If there is a message to send on Serial, it picks it up, and sends it.
		last_serial_read = None
		#broadcast_to_display_database = broadcast([display_data(), update_database()])
		while 1:
			if last_serial_read == None or (time.time() - last_serial_read > 10): # only check Serial port at most every 4 seconds
				line = {'status':{'lastStateChange':'Never', 'systemRunning':'N', 'lastStateChange':0, 'millis':100000},
					    'parameters':{'mode':0, 'temp':77, 'humidity':55},
					    'readings':{'temp':78, 'humidity':55}}
				last_serial_read = time.time()
				if line:
					#broadcast_to_display_database.send(line)
					pass
			try:
				parameter = queue.get(False) #non-blocking read. If empty, we handle the exception below
			except Queue.Empty:
				pass
			else:
				print(parameter)
			time.sleep(.25)
	finally:
		pass

# if called directly from the command line, then execute the main() function
if __name__ == "__main__":
	main()
