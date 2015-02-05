'''
This code checks whether the Climaduino parameters should be changed based on
day of the week and time of day.

It will be triggered at regular intervals. The code will not check for the exact time,
but will rather adjust for whatever the interval it is using is. So, if a 5 minute interval
is being used, it is 11:02, and the programming called for the temperature to change at 11,
it will still be changed.

The code will directly read the database using Django libraries.
'''

from django.core.management.base import BaseCommand, CommandError
from settings.models import Device, Setting, Program
import datetime, os, time

class Command(BaseCommand):
	args = 'There are no args!'
	help = 'Programming Sentry in charge of making sure programmed setting changes are executed'

	def handle(self, *args, **options):
		# BUG: Does not work when interval wraps around between days. If interval is 5 minutes
		# then times between 23:55 and 00:00 (midnight) do not work properly
		interval_in_seconds=300
		# set process niceness value to lower its priority
		os.nice(1)
				

		print("Climaduino Programming Sentry Started")
		while 1:
			print("Programming: Checking")
			now = datetime.datetime.now()

			# find out the day 0 is Monday
			current_day = now.weekday()

			# find out the time
			current_time = now.time()

			# calculate the time minus interval_in_seconds
			earliest_time = now - datetime.timedelta(seconds=interval_in_seconds)
			earliest_time = earliest_time.time()

			# query DB with interval_in_seconds "fudge factor"
			program_query = Program.objects.filter(day=current_day, time__range=(earliest_time, current_time))
			# if program exists, find out what should be changed and then change it
			for program in program_query:
				setting = Setting.objects.filter(device=program.device).last()
				# only make changes to device if it is alreay in the mode in the program
				if setting.mode == program.mode:
					print(program)
					print("Programming: Setting record")
					setting.time = now
					setting.source = 3
					# setting.mode = program.mode
					setting.temperature = program.temperature
					setting.humidity = program.humidity
					setting.save()

			# sleep for interval_in_seconds so we only check once during that interval
			time.sleep(interval_in_seconds)

# if called directly from the command line
if __name__ == "__main__":
	print("Can not be run directly from the command line.")