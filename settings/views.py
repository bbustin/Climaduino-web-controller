from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from settings.models import Setting, Reading, Program, change_parameter

class SettingForm(ModelForm):
	class Meta:
		model = Setting
		#fields = ['mode']
		fields=['mode']

class TemperatureForm(ModelForm):
	class Meta:
		model = Setting
		fields = ['temperature']

class HumidityForm(ModelForm):
	class Meta:
		model = Setting
		fields = ['humidity']

# class ProgrammingForm(ModelForm):
# 	class Meta:
# 		model = Program
# 		fields = ['mode', 'day', 'time', 'temperature', 'humidity']

def index(request):
	previous_setting = Setting.objects.last()
	if request.method == 'POST':
		form = SettingForm(request.POST)
		if form.is_valid():
			if 'mode' in form.cleaned_data:
				mode = form.cleaned_data['mode']
				change_parameter("%sM" % mode)
				setting_record = Setting(time=timezone.now(), source=1, mode=mode, temperature=previous_setting.temperature, humidity=previous_setting.humidity)
				setting_record.save()
		return HttpResponseRedirect(reverse('settings:index'))
	elif request.method == 'GET':
		current_readings = Reading.objects.last()
		form = SettingForm(instance=previous_setting)
		return render(request, 'settings/index.html',
			{'form': form,
			 'readings': current_readings,
			 'settings': previous_setting})

def set_temperature(request):
	previous_setting = Setting.objects.last()
	if request.method == 'POST':
		form = TemperatureForm(request.POST)
		if form.is_valid():
			if 'temperature' in form.cleaned_data:
				temperature = form.cleaned_data['temperature']
				change_parameter("%sF" % temperature)
				setting_record = Setting(time=timezone.now(), source=1, mode=previous_setting.mode, temperature=temperature, humidity=previous_setting.humidity)
				setting_record.save()
		return HttpResponseRedirect(reverse('settings:index'))
	if request.method == 'GET':
		return render(request, 'settings/individual.html',
			{'action': 'temperature',
			 'form_value': previous_setting.temperature}
			)

def set_humidity(request):
	previous_setting = Setting.objects.last()
	if request.method == 'POST':
		form = HumidityForm(request.POST)
		if form.is_valid():
			if 'humidity' in form.cleaned_data:
				humidity = form.cleaned_data['humidity']
				change_parameter("%s%%" % humidity)
				setting_record = Setting(time=timezone.now(), source=1, mode=previous_setting.mode, temperature=previous_setting.temperature, humidity=humidity)
				setting_record.save()
		return HttpResponseRedirect(reverse('settings:index'))
	if request.method == 'GET':
		return render(request, 'settings/individual.html',
			{'action': 'humidity',
			 'form_value': previous_setting.humidity}
			)

# def programming(request):
# 	programs = Program.objects
# 	if request.method == 'POST':
# 		formset = formset_factory(ProgrammingForm)
# 		if programming_formset.is_valid():
# 			print("Do something!")
# 		return HttpResponseRedirect(reverse('settings:programming'))
# 	elif request.method == 'GET':
# 		formset = formset_factory(ProgrammingForm)
# 		return render(request, 'settings/index.html',
# 		{'form': formset,})

	