import paho.mqtt.client as mqtt
import os, time

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
    print(data)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

def main(queue):
	import Queue
	# set process niceness value to lower its priority
	os.nice(1)
	print("Climaduino Controller started")
	client.connect("test.mosquitto.org", 1883, 60)
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
			print("Do something here...")
		client.loop(timeout=1)

		time.sleep(.5)

# if called directly from the command line, then execute the main() function
if __name__ == "__main__":
	print("Must be called from a program.")