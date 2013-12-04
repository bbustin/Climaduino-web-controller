from django.db import models

class Setting(models.Model):
	time = models.DateTimeField('last change')
	source_choices = ((0, 'Controller'),(1, 'Web Interface'), (3, 'Program'))
	source = models.IntegerField('source of last change', choices=source_choices, default=0)
	mode_choices = ((0, 'Cooling/Humidity Control'), (1, 'Humidity Control'), (5, 'Heating'), (9, 'Off'))
	mode = models.IntegerField(choices=mode_choices, default=0)
	temperature = models.IntegerField(default=77)
	humidity = models.IntegerField(default=55)
	def __unicode__(self):
		return("%s - \n\tmode: %d\n\ttemperature: %d\n\thumidity: %d" % (self.time, self.mode, self.temperature, self.humidity))

class Reading(models.Model):
	time = models.DateTimeField('last change')
	temperature = models.IntegerField()
	humidity = models.IntegerField()
	def __unicode__(self):
		return("%s - Readings:\n\ttemperature: %d\n\thumidity: %d" % (self.time, self.temperature, self.humidity))

class Program(models.Model):
	mode_choices = ((0, 'Cooling/Humidity Control'), (1, 'Humidity Control'), (5, 'Heating'), (9, 'Off'))
	mode = models.IntegerField(choices=mode_choices, default=0)
	time = models.TimeField()
	day_choices =((0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday"))
	day = models.IntegerField(choices=day_choices)
	temperature = models.IntegerField()
	humidity = models.IntegerField()
	def __unicode__(self):
		return("%s, %s - Program:\n\ttemperature: %d\n\thumidity: %d" % (self.day, self.time, self.temperature, self.humidity))
	# prevent creating more than 1 program for any specific day of week/time combination
	class Meta:
		unique_together = ('mode', 'day', 'time',)

## Trying to create a controller thread slowed down page generation responsiveness dramatically
# Maybe not the right place for this, but import the threading library and climaduiono-controller
# then thread out the main() function of climaduiono-controller
# import threading, climaduino_controller
# thread = threading.Thread(target=climaduino_controller.main)
# thread.setDaemon(True)
# thread.start()

# Create a process running the climaduino controller
import multiprocessing


# uncomment only one of the next two lines depending on whether in production mode or not
#import climaduino_controller_mock as climaduino_controller #for debugging on a different system
import climaduino_controller #for production
queue = multiprocessing.Queue()
controller_process = multiprocessing.Process(target=climaduino_controller.main, name="Climaduino Controller", args=[queue])
controller_process.daemon = True
controller_process.start()

import climaduino_programming_sentry
program_process = multiprocessing.Process(target=climaduino_programming_sentry.main, name="Programming Sentry", args=[queue, 300])
program_process.daemon = True
program_process.start()

def change_parameter(parameter):
	queue.put(parameter)