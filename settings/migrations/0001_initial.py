# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('name', models.CharField(max_length=30, serialize=False, verbose_name=b'Yun hostname', primary_key=True)),
                ('zonename', models.CharField(max_length=30, verbose_name=b'zone name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mode', models.IntegerField(default=0, choices=[(0, b'Cooling/Humidity Control'), (1, b'Humidity Control'), (5, b'Heating'), (9, b'Off')])),
                ('time', models.TimeField()),
                ('day', models.IntegerField(choices=[(0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday'), (6, b'Sunday')])),
                ('temperature', models.IntegerField()),
                ('humidity', models.IntegerField()),
                ('device', models.ForeignKey(to='settings.Device')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reading',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(verbose_name=b'last change')),
                ('temperature', models.DecimalField(max_digits=5, decimal_places=2)),
                ('humidity', models.DecimalField(max_digits=5, decimal_places=2)),
                ('device', models.ForeignKey(to='settings.Device')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(verbose_name=b'last change')),
                ('source', models.IntegerField(default=0, verbose_name=b'source of last change', choices=[(0, b'Climaduino'), (1, b'Controller'), (3, b'Program')])),
                ('mode', models.IntegerField(default=0, choices=[(0, b'Cooling'), (1, b'Humidity Control'), (5, b'Heating'), (9, b'Off')])),
                ('fanMode', models.BooleanField(default=False)),
                ('temperature', models.IntegerField(default=77)),
                ('humidity', models.IntegerField(default=55)),
                ('currentlyRunning', models.BooleanField(default=False)),
                ('stateChangeAllowed', models.BooleanField(default=False)),
                ('device', models.ForeignKey(to='settings.Device')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('currentlyRunning', models.BooleanField(default=False)),
                ('stateChangeAllowed', models.BooleanField(default=False)),
                ('device', models.ForeignKey(to='settings.Device')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='program',
            unique_together=set([('device', 'mode', 'day', 'time')]),
        ),
    ]
