from django.db import models
import json, socket

def send_settings(data):
	# Connect to the server
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect('/tmp/climaduino_mqtt_bridge')
	s.send(json.dumps(data))
	s.close()

class Device(models.Model):
	name = models.CharField("Yun hostname", max_length=30, primary_key=True)
	zonename = models.CharField("zone name", max_length=30)
	def __unicode__(self):
		return("%s (%s)" % (self.zonename, self.name))

class Setting(models.Model):
	device = models.ForeignKey("Device")
	time = models.DateTimeField('last change')
	source_choices = ((0, 'Climaduino'),(1, 'Controller'), (3, 'Program'))
	source = models.IntegerField('source of last change', choices=source_choices, default=0)
	mode_choices = ((0, 'Cooling'), (1, 'Humidity Control'), (5, 'Heating'), (9, 'Off'))
	mode = models.IntegerField(choices=mode_choices, default=0)
	fanMode = models.BooleanField(default=False)
	temperature = models.IntegerField(default=77)
	humidity = models.IntegerField(default=55)
	def __unicode__(self):
		return("%s - \n\tmode: %d\n\ttemperature: %d\n\thumidity: %d" % (self.time, self.mode, self.temperature, self.humidity))
	def save(self, *args, **kwargs):
		# send the settings to the mqtt_bridge so the Climaduino will receive them
		send_settings({self.device.name: {'settings': {'mode': self.mode, 'fanMode': self.fanMode, 'tempSetPoint': self.temperature, 'humiditySetPoint': self.humidity}}})
		super(Setting, self).save(*args, **kwargs) # save the DB record

class Status(models.Model):
	device = models.ForeignKey("Device")
	time = models.DateTimeField('last change')
	currentlyRunning = models.BooleanField(default=False)
	stateChangeAllowed = models.BooleanField(default=False)
	def __unicode__(self):
		return("- \n\tcurrentlyRunning: %s\n\tstateChangeAllowed: %s" % (self.currentlyRunning, self.stateChangeAllowed))

class Reading(models.Model):
	device = models.ForeignKey("Device")
	time = models.DateTimeField('last change')
	temperature = models.DecimalField(max_digits=5, decimal_places=2)
	humidity = models.DecimalField(max_digits=5, decimal_places=2)
	def __unicode__(self):
		return("%s - Readings:\n\ttemperature: %d\n\thumidity: %d" % (self.time, self.temperature, self.humidity))

class Program(models.Model):
	device = models.ForeignKey("Device")
	mode_choices = ((0, 'Cooling/Humidity Control'), (1, 'Humidity Control'), (5, 'Heating'), (9, 'Off'))
	mode = models.IntegerField(choices=mode_choices, default=0)
	time = models.TimeField()
	day_choices =((0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday"))
	day = models.IntegerField(choices=day_choices)
	temperature = models.IntegerField()
	humidity = models.IntegerField()
	def __unicode__(self):
		return("%s: %s at %s, %s, temperature: %d humidity: %d" % (self.device, self.get_day_display(), self.time, self.get_mode_display(), self.temperature, self.humidity))
	# prevent creating more than 1 program for any specific day of week/time combination for any device
	class Meta:
		unique_together = ('device', 'mode', 'day', 'time',)
