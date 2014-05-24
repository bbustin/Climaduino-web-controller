from django.db import models
try:
	import rrdtool_log
except ImportError:
	pass

class Device(models.Model):
	identifier = models.IntegerField(primary_key=True)
	name = models.CharField("device name", max_length=30)
	def __unicode__(self):
		return("%s (%d)" % (self.name, self.identifier))

class Setting(models.Model):
	device = models.ForeignKey("Device")
	time = models.DateTimeField('last change')
	source_choices = ((0, 'Climaduino'),(1, 'Controller'), (3, 'Program'))
	source = models.IntegerField('source of last change', choices=source_choices, default=0)
	mode_choices = ((0, 'Cooling/Humidity Control'), (1, 'Humidity Control'), (5, 'Heating'), (9, 'Off'))
	mode = models.IntegerField(choices=mode_choices, default=0)
	temperature = models.IntegerField(default=77)
	humidity = models.IntegerField(default=55)
	def __unicode__(self):
		return("%s - \n\tmode: %d\n\ttemperature: %d\n\thumidity: %d" % (self.time, self.mode, self.temperature, self.humidity))

class Reading(models.Model):
	device = models.ForeignKey("Device")
	time = models.DateTimeField('last change')
	temperature = models.IntegerField()
	humidity = models.IntegerField()
	def __unicode__(self):
		return("%s - Readings:\n\ttemperature: %d\n\thumidity: %d" % (self.time, self.temperature, self.humidity))
	# overriding save so we can also log to rrdtool in addition to updating the DB
	def save(self, *args, **kwargs):
		try:
			rrdtool_log.main(self.device.identifier, self.temperature, self.humidity)
		except NameError:
			print("unable to log to rrdtool")
		super(Reading, self).save(*args, **kwargs) # save the DB record

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
		return("%s at %s, %s, temperature: %d humidity: %d" % (self.get_day_display(), self.time, self.get_mode_display(), self.temperature, self.humidity))
	# prevent creating more than 1 program for any specific day of week/time combination for any device
	class Meta:
		unique_together = ('device', 'mode', 'day', 'time',)