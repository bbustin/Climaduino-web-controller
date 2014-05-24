import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.forms import ModelForm
# from django.forms.formsets import formset_factory
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from settings.models import Device, Setting, Reading, Program

class SettingForm(ModelForm):
	class Meta:
		model = Setting
		fields=['mode']

class TemperatureForm(ModelForm):
	class Meta:
		model = Setting
		fields = ['temperature']

class HumidityForm(ModelForm):
	class Meta:
		model = Setting
		fields = ['humidity']

class ProgrammingForm(ModelForm):
	class Meta:
		model = Program
		fields = ['mode', 'day', 'time', 'temperature', 'humidity']

@csrf_exempt
def device_index(request, device_id):
	device = Device.objects.get(pk=device_id)
	setting = Setting.objects.filter(device__pk=device_id).last()
	if request.method == 'POST':
		form = SettingForm(request.POST)
		if form.is_valid():
			if 'mode' in form.cleaned_data:
				setting.mode = form.cleaned_data['mode']
				setting.save()
		return HttpResponseRedirect(reverse('settings:device_index', args=[device.identifier]))
	elif request.method == 'GET':
		current_readings = Reading.objects.filter(device__pk=device_id).last()
		form = SettingForm(instance=setting)
		return render(request, 'settings/device_index.html',
			{'form': form,
			 'readings': current_readings,
			 'settings': setting,
			 'device': device})

def index(request):
	devices = Device.objects.all()
	if request.method == 'GET':
		return render(request, 'settings/index.html',
			{'devices': devices})

def set_temperature(request, device_id):
	setting = Setting.objects.filter(device__pk=device_id).last()
	device = Device.objects.get(pk=device_id)
	if request.method == 'POST':
		form = TemperatureForm(request.POST)
		if form.is_valid():
			if 'temperature' in form.cleaned_data:
				setting.temperature = form.cleaned_data['temperature']
				setting.save()
		return HttpResponseRedirect(reverse('settings:device_index', args=[device.identifier]))
	if request.method == 'GET':
		return render(request, 'settings/individual.html',
			{'action': 'temperature',
			 'form_value': setting.temperature,
			 'device': device,
			 'url_namespace': 'settings:temperature'}
			)

def set_humidity(request, device_id):
	setting = Setting.objects.filter(device__pk=device_id).last()
	device = Device.objects.get(pk=device_id)
	if request.method == 'POST':
		form = HumidityForm(request.POST)
		if form.is_valid():
			if 'humidity' in form.cleaned_data:
				setting.humidity = form.cleaned_data['humidity']
				setting.save()
		return HttpResponseRedirect(reverse('settings:device_index', args=([device.identifier])))
	if request.method == 'GET':
		return render(request, 'settings/individual.html',
			{'action': 'humidity',
			 'form_value': setting.humidity,
			 'device': device,
			 'url_namespace': 'settings:humidity'}
			)

def programs(request, device_id):
	program_records = Program.objects.order_by('day', 'time', 'mode')
	device = Device.objects.get(pk=device_id)
	if request.method == 'POST':
		form = ProgrammingForm(request.POST)
		if form.is_valid():
			program_record = Program(**form.cleaned_data)
			program_record.save()
		return HttpResponseRedirect(reverse('settings:programs'))
	elif request.method == 'GET':
		form = ProgrammingForm()
		return render(request, 'settings/programs.html',
		{'form': form,
		 'programs': program_records,
		 'device': device}
		)
	
@csrf_exempt
def climaduino(request, device_id):
	setting = Setting.objects.filter(device__pk=device_id).last()
	if request.method == 'POST':
		update_time = timezone.now()
		print 'Device ID: %s' % device_id
		print 'Data: %s' % request.body
		try:
			json_object = json.loads(request.body)
		except ValueError:
			print("Not valid JSON")
			json_object = None
		else:
			print('JSON: %s' % json_object)
		print('Previous Setting: %s' % setting)
		response_string = "^" #delimeter to indicate this is where Climaduino should start its parsing
		# if we get valid data from the Climaduino
		if json_object:
			# if we have a previous setting, compare to the data from the Climaduino
			## then determine what to do. Right now, overwrite Climaduino as it is just a remote
			## need way for Climaduino with display to not be overwritten when temp set locally on it
			if setting:
				if setting.mode != json_object['parameters']['mode']:
					response_string = "%s%sM" % (response_string, setting.mode)
				if setting.temperature != json_object['parameters']['temp']:
				 	response_string = "%s%sF" % (response_string, setting.temperature)
				if setting.humidity != json_object['parameters']['humidity']:
					response_string = "%s%s%%" % (response_string, setting.humidity)
			# update the current readings
			# Round current temperature and humidity readings
			temperature_rounded = round(json_object["readings"]["temp"])
			humidity_rounded = round(json_object["readings"]["humidity"])
			try:
				reading = Reading.objects.filter(device__pk=device_id).last()
			except Reading.DoesNotExist:
				reading = Reading(device_id=device_id, time=update_time, temperature=temperature_rounded, humidity=humidity_rounded)
			else:
				reading.time = update_time
				reading.temperature = temperature_rounded
				reading.humidity = humidity_rounded
			reading.save()

	return(HttpResponse(response_string))
