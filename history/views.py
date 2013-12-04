from django.shortcuts import render
import graphs

def index(request):
	# create graphs and get list of file names
	file_paths = graphs.create_graphs()
	# create a template that shows each graph image
	# render the template
	return render(request, 'history/index.html',
		{'graphs': file_paths})
