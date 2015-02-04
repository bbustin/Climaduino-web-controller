from django.shortcuts import render
from settings.models import Device
import graphs

def index(request, device_name):
	device = Device.objects.get(pk=device_name)
	# create graphs and get list of file names
	file_paths = graphs.create_graphs(device_name)
	# create a template that shows each graph image
	# render the template
	return render(request, 'history/index.html',
		{'graphs': file_paths,
		'device': device})
