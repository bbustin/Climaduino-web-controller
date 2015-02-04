graph_type = {}
time_periods = ["15m", "30m", "2h", "1d", "1w", "1m", "1y", "4y"]

# if cannot import rrdtool, then we will not generate any graphs when create_graphs called
try:
	import rrdtool
except:
	print("python-rrdtool library is not installed. Graphs will not be available.")

def create_graphs(device_name):
	rrd_file = "temp_humidity-%s.rrd" % device_name

	graph_type = {}
	graph_type["temperature"] = {'data_sources': ['DEF:temperatureAvg=%s:temperature:AVERAGE' % rrd_file,
												  'DEF:temperatureSet=%s:temperatureSetPoint:AVERAGE' % rrd_file,
												  #'DEF:temperatureMax=%s:temperature:MAX' % rrd_file,
												  #'DEF:temperatureMin=%s:temperature:MIN % rrd_file'
												  ],
								'graph_elements': ['LINE1:temperatureAvg#0000FF:Temp Avg\r',
												   'LINE1:temperatureSet#000000:Temp Set\r',
												   #'LINE1:temperatureMax#00FF00:TemperatureMax\r',
												   #'LINE1:temperatureMin#FF0000:TemperatureMin\r'
												   ]}
	graph_type["humidity"] = {'data_sources': ['DEF:humidityAvg=%s:humidity:AVERAGE' % rrd_file,
											   'DEF:humiditySet=%s:humiditySetPoint:AVERAGE' % rrd_file,
											   #'DEF:humidityMax=%s:humidity:MAX' % rrd_file,
											   #'DEF:humidityMin=%s:humidity:MIN' % rrd_file
											   ],
							'graph_elements': ['LINE1:humidityAvg#0000FF:Hum Avg\r',
											   'LINE1:humiditySet#000000:Hum Set\r',
											   #'LINE1:humidityMax#00FF00:Humidity Max\r',
											   #'LINE1:humidityMin#FF0000:Humidity Min\r'
											   ]}

	image_names = [] #keep track of all image paths so we can return it to caller

	for graph in graph_type:
		for time_period in time_periods:
			image_name = "graph-%s-%s-%s.png" % (device_name, graph, time_period)
			image_names.append(image_name)
			rrdtool.graph("./history/static/%s" % image_name,
				"--start", "-%s" % time_period,
				graph_type[graph]['data_sources'],
				graph_type[graph]['graph_elements'])
	return(image_names)



if __name__ == "__main__":
	create_graphs()