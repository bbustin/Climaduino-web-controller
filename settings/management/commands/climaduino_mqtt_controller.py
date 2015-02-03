from django.core.management.base import BaseCommand, CommandError
from settings.models import Device, Setting, Reading
from django.utils import timezone

import paho.mqtt.client as mqtt
import os, time

import SocketServer, threading, socket

class Command(BaseCommand):
	args = 'There are no args!'
	help = 'Starts up communication with Climaduinos via the MQTT broker'

	def handle(self, *args, **options):
		self.stdout.write("Climaduino Controller started")

		connected = False
		tries = 0
		while not connected and tries <= 20:
			tries += 1
			try:
				address = ('localhost', 64000) # let the kernel give us a port
				server = SocketServer.TCPServer(address, ReceiveSettingsHandler)
				(ip, port) = server.server_address # find out what port we were given
				t = threading.Thread(target=server.serve_forever)
				t.setDaemon(True) # don't hang on exit
				t.start()
			except socket.error:
				self.stdout.write("Error starting server. Will retry shortly.")
				time.sleep(5)
			else:
				connected = True
		self.stdout.write("Listening for setting changes at {}:{}".format(ip, port))

		# The callback for when the client receives a CONNACK response from the server.
		def on_connect(client, userdata, flags, rc):
			# Subscribing in on_connect() means that if we lose the connection and
			# reconnect then subscriptions will be renewed.
			client.subscribe("climaduino/+/readings/#")
			client.subscribe("climaduino/+/status/#")

		# The callback for when a PUBLISH message is received from the server.
		def on_message(client, userdata, msg):
			(device, category, item) = msg.topic.replace("climaduino/", "").split("/", 2)
			data = {device: {category: {item: msg.payload}}}
			database_update(data)
			self.stdout.write(str(data))

		client = mqtt.Client()
		client.on_connect = on_connect
		client.on_message = on_message
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
			data_status = data[device]['status']
		except KeyError:
			pass # no status to update
		else:
			# update status information
			setting = Setting.objects.filter(device__pk=device).last()
			if not setting:
				setting = Setting(device=device_object, time=update_time, mode=0, fanMode=0, temperature=0, humidity=0, currentlyRunning=0, stateChangeAllowed=0)
			setting.time = update_time
			setting.source = 0
			for attribute in data_status:
				setattr(setting, attribute, data_status[attribute])
			setting.save()

class ReceiveSettingsHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # Echo the back to the client
        data = self.request.recv(1024)
        print("GOT DATA!!!!!!!")
        print(data)
        return

# if called directly from the command line, then execute the main() function
if __name__ == "__main__":
	print("Must be called from a program.")