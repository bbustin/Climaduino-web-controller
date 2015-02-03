# TODO: Detect when connection to broker lost and reconnect!
from django.core.management.base import BaseCommand, CommandError
from settings.models import Device, Status, Setting, Reading
from django.utils import timezone

import paho.mqtt.client as mqtt
import os, time

import json

import SocketServer, threading, socket

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("climaduino/+/readings/#")
	client.subscribe("climaduino/+/status/#")
	self.stdout.write("Connected to MQTT broker")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	(device, category, item) = msg.topic.replace("climaduino/", "").split("/", 2)
	data = {device: {category: {item: msg.payload}}}
	database_update(data)
	print(str(data))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Connection to MQTT broker unexpectedly lost")
        connected = False
        while not connected:
	        try:
	        	client.reconnect()
	        except (socket.gaierror, socket.error):
	        	print("Reconnection failed. Will try again shortly.")
	        	time.sleep(30)
	        else:
	        	connected = True
	        	print("Reconnected")
	else:
		print("Disconnected from MQTT broker")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

class Command(BaseCommand):
	args = 'There are no args!'
	help = 'Starts up communication with Climaduinos via the MQTT broker'

	def handle(self, *args, **options):
		self.stdout.write("Climaduino Controller started")
		socket_address = ('/tmp/climaduino_mqtt_bridge')

		# clean up stale socket if there is one
		try:
			os.remove(socket_address)
		except OSError:
			pass

		connected = False
		tries = 0
		while not connected and tries <= 20:
			tries += 1
			try:
				server = SocketServer.UnixStreamServer(socket_address, ReceiveSettingsHandler)
				t = threading.Thread(target=server.serve_forever)
				t.setDaemon(True) # don't hang on exit
				t.start()
			except socket.error as error:
				self.stdout.write("Error starting server. Will retry shortly.\n\t{}".format(error))
				time.sleep(5)
			else:
				connected = True

		if not connected:
			raise Exception("Unable to listen for setting changes")

		self.stdout.write("Listening for setting changes on socket {}".format(socket_address))

		client.connect("test.mosquitto.org", 1883, 60)
		# print results from all Climaduinos and update DB
		last_poll = time.time()
		while 1:
			# if (time.time() - last_poll >= poll_interval_seconds):
			# 	last_poll = time.time()
			# 	# get data to set
			# 	items_available = True
			# 	data_item={}
			# 	while items_available:
			# 		try:
			# 			item = queue.get(False) #non-blocking read
			# 		except Queue.Empty:
			# 			items_available = False
			# 		else:
			# 			data_item.update(item)
			# 	if len(data_item)>0:
			# 		database_update(data_item)
			# 		# for device in data_item:
			# 		# 	# pseudo-code for now...
			# 		# 	print(device)
			# 		# 	print("\t-{}".format(data_item))
			client.loop(timeout=1)

			time.sleep(.5)


def database_update(data):
	update_time = timezone.now()

	# when there is reading data to update
	for device in data:
		device_object = Device.objects.filter(name=device).last()
		if not device_object:
			device_object = Device(name=device, zonename="Auto-added ({})".format(device))
			device_object.save()

		try:
			data_reading = data[device]['readings']
		except KeyError:
			pass #no readings to update
		else:
			# update reading
			reading = Reading.objects.filter(device__pk=device).last()
			if not reading:
				reading = Reading(device=device_object, time=update_time, temperature=0, humidity=0)
			reading.time = update_time
			for attribute in data_reading:
				setattr(reading, attribute, data_reading[attribute])
			reading.save()
			
		try:
			data_settings = data[device]['settings']
		except KeyError:
			pass # no status to update
		else:
			# update status information
			setting = Setting.objects.filter(device__pk=device).last()
			if not setting:
				setting = Setting(device=device_object, time=update_time, mode=0, fanMode=0, temperature=0, humidity=0)
			setting.time = update_time
			setting.source = 0
			for attribute in data_settings:
				setattr(setting, attribute, data_settings[attribute])
			setting.save()


		try:
			data_status = data[device]['status']
		except KeyError:
			pass # no status to update
		else:
			# update status information
			status = Status.objects.filter(device__pk=device).last()
			if not status:
				status = Status(device=device_object, time=update_time, currentlyRunning=0, stateChangeAllowed=0)
			status.time = update_time
			status.source = 0
			for attribute in data_status:
				setattr(status, attribute, data_status[attribute])
			status.save()

class ReceiveSettingsHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		# Echo the back to the client
		data = json.loads(self.request.recv(1024))
		for device in data:
			try:
				for (key, value) in data[device]['settings'].items():
					# Convert boolean values to 0 and 1
					if isinstance(value, bool):
						value = int(value)
					client.publish('climaduino/{}/settings/{}'.format(device, key), value)
					time.sleep(0.1) # does not seem to work reliably without a slight pause
			except KeyError:
				print("Invalid data received: {}".format(data))
		print(data)
		return

# if called directly from the command line, then execute the main() function
if __name__ == "__main__":
	print("Must be called from a program.")