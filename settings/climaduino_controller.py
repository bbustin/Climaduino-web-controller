import requests, time

## Django stuff
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'climaduino.settings'
import models
from django.utils import timezone
import django
# to maintain backwards compatibility with Django 1.6
try:
	django.setup()
except AttributeError:
	pass
##
def database_update(device_id, temperature, humidity, tempSetPoint, humiditySetPoint, mode, fanMode, currentlyRunning, stateChangeAllowed):
	update_time = timezone.now()

	# update reading
	reading = models.Reading.objects.filter(device__pk=device_id).last()
	if not reading:
		reading = models.Reading(device_id=device_id, time=update_time, temperature=temperature, humidity=humidity)
	else:
		reading.time = update_time
		reading.temperature = temperature
		reading.humidity = humidity
	reading.save()

	# update setting
	setting = models.Setting.objects.filter(device__pk=device_id).last()
	if not setting:
		setting = models.Setting(device_id=device_id, time=update_time, source=0, mode=mode, fanMode=fanMode, temperature=tempSetPoint, humidity=humiditySetPoint, currentlyRunning=currentlyRunning, stateChangeAllowed=stateChangeAllowed)
	else:
		setting.time = update_time
		setting.source = 0
		setting.mode = mode
		setting.fanMode = fanMode
		setting.temperature = tempSetPoint
		setting.humidity = humiditySetPoint
		setting.currentlyRunning = currentlyRunning
		setting.stateChangeAllowed = stateChangeAllowed
	setting.save()

def climaduino_poll(device_name):
	url = "http://{}.local/data/get".format(device_name)
	try:
		request = requests.get(url)
		request.raise_for_status()
	except (requests.exceptions.HTTPError, requests.exceptions.Timeout, requests.exceptions.ConnectionError) as details:
		print("{} - Failed to poll: {}".format(device_name, details))
		return(None)
	return(request.json()['value'])

def climaduino_set_parameters(device_name, parameters):
	url_base = "http://{}.local/data/put".format(device_name)
	for parameter in parameters:
		url = "{}/{}/{}".format(url_base, parameter, parameters[parameter])
		try:
			request = requests.get(url)
			request.raise_for_status()
		except (requests.exceptions.HTTPError, requests.exceptions.Timeout, requests.exceptions.ConnectionError) as details:
			print("{} - Failed to set '{}' parameter: {}".format(device_name, parameter, details))
		else:
			print("{} - Set '{}' parameter: {}".format(device_name, parameter, parameters[parameter]))

def main(queue, climaduino_poll_interval_in_seconds):
	import Queue
	# set process niceness value to lower its priority
	os.nice(1)
	print("Climaduino Controller started")
	# print results from all Climaduinos and update DB
	last_poll = time.time()
	while 1:
		# get data to set
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
			device = models.Device.objects.get(pk=data_item['device_id'])
			try:
				climaduino_set_parameters(device.name, {'tempSetPoint': data_item['parameters']['temp'],
														'humiditySetPoint': data_item['parameters']['humidity'],
														'mode': data_item['parameters']['mode'],
														'fanMode': int(data_item['parameters']['fanMode'])})
			except KeyError as details:
				print("{} - Unable to update Climaduino: {}".format(device.name, details))
		if (time.time() - last_poll >= climaduino_poll_interval_in_seconds):
			last_poll = time.time()
			for device in models.Device.objects.all():
				values = climaduino_poll(device.name)
				if values:
					print(values)
					try:
						database_update(device.identifier, float(values['temperature']), float(values['humidity']), int(values['tempSetPoint']), int(values['humiditySetPoint']), int(values['mode']), int(values['fanMode']), int(values['currentlyRunning']), int(values['stateChangeAllowed']))
					except KeyError as details:
						print("{} - Unable to update database: {}".format(device.name, details))
					# clear queue, otherwise will try to send the setpoints and mode to the Arduino even though that is just where we got the information
					items_available = True
					while items_available:
						try:
							queue.get(False) #non-blocking read
						except Queue.Empty:
							items_available = False
		time.sleep(.5)

	# print("setting parameters")
	# climaduino_set_parameters("climaduinohouse", {'tempSetPoint': 86, 'humiditySetPoint': 58, 'mode': 9})

# if called directly from the command line, then execute the main() function
if __name__ == "__main__":
	print("Must be called from a program.")
