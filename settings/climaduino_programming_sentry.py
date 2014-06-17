'''
This code checks whether the Climaduino parameters should be changed based on
day of the week and time of day.

It will be triggered at regular intervals. The code will not check for the exact time,
but will rather adjust for whatever the interval it is using is. So, if a 5 minute interval
is being used, it is 11:02, and the programming called for the temperature to change at 11,
it will still be changed.

The code will directly read the database using Django libraries.
'''

## Django stuff
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'climaduino.settings'
import models

import time, datetime
##

def main(interval_in_seconds=300):
   # BUG: Does not work when interval wraps around between days. If interval is 5 minutes
   # then times between 23:55 and 00:00 (midnight) do not work properly

   # set process niceness value to lower its priority
	os.nice(1)
	print("Climaduino Programming Sentry Active")
	while 1:
		print("Programming: Checking")
	   	now = datetime.datetime.now()
	   	current_settings = models.Setting.objects.last()
	   	# find out the day 0 is Monday
	   	current_day = now.weekday()

	   	# find out the time
	   	current_time = now.time()

	   	# calculate the time minus interval_in_seconds
	   	earliest_time = now - datetime.timedelta(seconds=interval_in_seconds)
	   	earliest_time = earliest_time.time()

	   	# query DB with interval_in_seconds "fudge factor"
	   	program_query = models.Program.objects.filter(mode=current_settings.mode, day=current_day, time__range=(earliest_time, current_time))
	   	print(program_query)
	   	# if program exists, find out what should be changed and then change it
	   	for program in program_query:
	   		print("Programming: Setting record")
	   		setting = models.Setting.objects.filter(device__pk=program.device_id).last()
	   		setting.time = now
	   		setting.source = 3
	   		setting.mode = program.mode
	   		setting.temperature = program.temperature
	   		setting.humidity = program.humidity
	   		setting.save()

	   	# sleep for interval_in_seconds so we only check once during that interval
	   	time.sleep(interval_in_seconds)

# if called directly from the command line
if __name__ == "__main__":
	print("Can not be run directly from the command line.")