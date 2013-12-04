from django.contrib import admin
from settings.models import Setting, Reading, Program

class SettingAdmin(admin.ModelAdmin):
	list_filter = ['time', 'source']
	list_display = ('time', 'source', 'temperature', 'humidity', 'mode')

class ReadingAdmin(admin.ModelAdmin):
	list_filter = ['time']
	list_display = ('time', 'temperature', 'humidity')

class ProgramAdmin(admin.ModelAdmin):
	list_filter = ['mode', 'day', 'time']
	list_display = ['mode', 'day', 'time', 'temperature', 'humidity']

admin.site.register(Setting, SettingAdmin)
admin.site.register(Reading, ReadingAdmin)
admin.site.register(Program, ProgramAdmin)