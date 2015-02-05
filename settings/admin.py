from django.contrib import admin
from settings.models import Setting, Reading, Program, Device, Status

class SettingAdmin(admin.ModelAdmin):
	list_filter = ['device', 'time', 'source']
	list_display = ['device' ,'time', 'source', 'temperature', 'humidity', 'mode']

class ReadingAdmin(admin.ModelAdmin):
	list_filter = ['device', 'time']
	list_display = ('device', 'time', 'temperature', 'humidity')

class ProgramAdmin(admin.ModelAdmin):
	list_filter = ['device', 'mode', 'day', 'time']
	list_display = ['device', 'mode', 'day', 'time', 'temperature', 'humidity']

class DeviceAdmin(admin.ModelAdmin):
	list_display = ['zonename', 'name']

class StatusAdmin(admin.ModelAdmin):
	list_display = ['currentlyRunning', 'stateChangeAllowed']
	readonly_fields=['currentlyRunning', 'stateChangeAllowed']

admin.site.register(Setting, SettingAdmin)
admin.site.register(Reading, ReadingAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Status, StatusAdmin)