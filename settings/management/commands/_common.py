# Common abstractions for dealing with MQTT and SocketServer
import SocketServer, threading, socket
import paho.mqtt.client as mqtt
import os, time
import json

class BridgeServer(object):
	def __init__(self):
		pass

	def __del__(self):
		try:
			mqtt_stop()
		except:
			pass

	def mqtt_start(self, mqtt_broker_host, mqtt_broker_port=1883, mqtt_keepalive=60):
		self.mqtt_client = mqtt.Client()

		# register handlers
		self.mqtt_client.on_disconnect = self.mqtt_disconnect
		self.mqtt_client.on_connect = self.mqtt_connect
		self.mqtt_client.on_message = self.mqtt_message

		self.mqtt_client.connect(mqtt_broker_host, mqtt_broker_port, mqtt_keepalive)
		self.mqtt_client.loop_start()

	def mqtt_stop(self):
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()

	def socket_start(self, socket_path, socket_data_handler):
		handler = self._SocketRequestHandler
		handler.user_handler = socket_data_handler

		# clean up stale socket if there is one
		try:
			os.remove(socket_path)
		except OSError:
			pass

		connected = False
		tries = 0
		while not connected and tries <= 20:
			tries += 1
			try:
				self.socket_server = SocketServer.UnixStreamServer(socket_path, handler)
				t = threading.Thread(target=self.socket_server.serve_forever)
				t.setDaemon(True) # don't hang on exit
				t.start()
			except socket.error as error:
				print("Error starting server. Will retry shortly.\n\t{}".format(error))
				time.sleep(5)
			else:
				connected = True

		if not connected:
			raise Exception("Unable to listen on socket {}".format(socket_path))

		print("Listening on socket {}".format(socket_path))

	## Socket Handler - do not override this one, instead pass a function for socket_data_handler during instantiation
	class _SocketRequestHandler(SocketServer.BaseRequestHandler):
		def handle(self):
			data = self.request.recv(1024)
			# pass data into user-supplied function
			self.user_handler(data)
			return

	## MQTT handlers - these can be overriden
	def mqtt_disconnect(self, client, userdata, rc):
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

	def mqtt_connect(self, client, userdata, flags, rc):
		print("Connected to MQTT broker")

	def mqtt_message(self, client, userdata, msg):
		print("{} => {}".format(msg.topic, msg.payload))