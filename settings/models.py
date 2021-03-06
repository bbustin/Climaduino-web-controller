from django.db import models
import rrdtool_log
import climaduino_programming_sentry
import climaduino_controller

class Device(models.Model):
	identifier = models.IntegerField(primary_key=True)
	name = models.CharField("device name - hostname of Arduino Yun", max_length=30)
	zonename = models.CharField("zone name", max_length=30)
	def __unicode__(self):
		return("%s (%d)" % (self.zonename, self.identifier))

class Setting(models.Model):
	device = models.ForeignKey("Device")
	time = models.DateTimeField('last change')
	source_choices = ((0, 'Climaduino'),(1, 'Controller'), (3, 'Program'))
	source = models.IntegerField('source of last change', choices=source_choices, default=0)
	mode_choices = ((0, 'Cooling/Humidity Control'), (1, 'Humidity Control'), (5, 'Heating'), (8, 'Fan Only'), (9, 'Off'))
	mode = models.IntegerField(choices=mode_choices, default=0)
	temperature = models.IntegerField(default=77)
	humidity = models.IntegerField(default=55)
	currentlyRunning = models.BooleanField(default=False)
	stateChangeAllowed = models.BooleanField(default=False)
	def __unicode__(self):
		return("%s - \n\tmode: %d\n\ttemperature: %d\n\thumidity: %d" % (self.time, self.mode, self.temperature, self.humidity))
	def log(self):
		queue.put({'device_id': self.device.identifier, 'parameters': {'temp': self.temperature, 'humidity': self.humidity}})
		queue_update_parameters.put({'device_id': self.device.identifier, 'parameters': {'temp': self.temperature, 'humidity': self.humidity, 'mode': self.mode}})		
	# overriding save so we can also log to rrdtool in addition to updating the DB
	def save(self, *args, **kwargs):
		self.log()
		super(Setting, self).save(*args, **kwargs) # save the DB record

class Reading(models.Model):
	device = models.ForeignKey("Device")
	time = models.DateTimeField('last change')
	temperature = models.DecimalField(max_digits=5, decimal_places=2)
	humidity = models.DecimalField(max_digits=5, decimal_places=2)
	def __unicode__(self):
		return("%s - Readings:\n\ttemperature: %d\n\thumidity: %d" % (self.time, self.temperature, self.humidity))
	def log(self):
		queue.put({'device_id': self.device.identifier, 'readings': {'temp': self.temperature, 'humidity': self.humidity}})
	# overriding save so we can also log to rrdtool in addition to updating the DB
	def save(self, *args, **kwargs):
		self.log()
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

# Create a process to log to rrd_tool
import multiprocessing
queue = multiprocessing.Queue()
logger_process = multiprocessing.Process(target=rrdtool_log.main, name="rrdtool logger", args=[queue, 4])
logger_process.daemon = True
logger_process.start()

queue_update_parameters = multiprocessing.Queue()
controller_process = multiprocessing.Process(target=climaduino_controller.main, name="climaduino controller", args=[queue_update_parameters, 15])
controller_process.daemon = True
controller_process.start()
programming_sentry_process = multiprocessing.Process(target=climaduino_programming_sentry.main, name="programming sentry", args=[60])
programming_sentry_process.daemon = True
programming_sentry_process.start()
