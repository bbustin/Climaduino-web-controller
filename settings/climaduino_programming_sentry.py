'''
This code checks whether the Climaduino parameters should be changed based on
day of the week and time of day.

It will be triggered at regular intervals. The code will not check for the exact time,
but will rather adjust for whatever the interval it is using is. So, if a 5 minute interval
is being used, it is 11:02, and the programming called for the temperature to change at 11,
it will still be changed.

The code will directly read the database using Django libraries. It will change parameters
using a queue that is passed in. The queue is used by the climaduino_controller which will
send the settings to the Climaduino.
'''

## Django stuff
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'climaduino.settings'
from models import Setting, Program
from django.utils import timezone
import time, datetime
##

def main(queue, interval_in_seconds=300):
	'''Queue is used to communicate with the climaduino_controller. Interval is
	   how often to check the database for program settings.'''
	   # BUG: Does not work when program set to change parameters on midnight (00:00)
	print("Climaduino Programming Sentry Active")
	while 1:
	   	now = datetime.datetime.now()
	   	current_settings = Setting.objects.last()
	   	# find out the day 0 is Monday
	   	current_day = now.weekday()

	   	# find out the time
	   	current_time = now.time()

	   	# calculate the time minus interval_in_seconds
	   	earliest_time = now - datetime.timedelta(seconds=interval_in_seconds)
	   	earliest_time = earliest_time.time()

	   	# query DB with interval_in_seconds "fudge factor"
	   	program_query = Program.objects.filter(mode=current_settings.mode, day=current_day, time__range=(earliest_time, current_time))

	   	# if program exists, find out what should be changed and then change it
	   	for program in program_query:
	   		setting_record = Setting(time=now, source=3, mode=program.mode, temperature=program.temperature, humidity=program.humidity)
	   		setting_record.save()
	   		if program.temperature != current_settings.temperature:
	   			queue.put("%sF" % program.temperature)
	   		if program.humidity != current_settings.humidity:
	   			queue.put("%s%%" % program.humidity)

	   	# sleep for interval_in_seconds so we only check once during that interval
	   	time.sleep(interval_in_seconds)

# if called directly from the command line
if __name__ == "__main__":
	print("Can not be run directly from the command line.")