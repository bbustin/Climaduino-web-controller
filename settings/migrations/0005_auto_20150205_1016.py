# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0004_auto_20150205_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='day',
            field=models.IntegerField(choices=[(0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday'), (6, b'Sunday')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='program',
            name='humidity',
            field=models.IntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='program',
            name='mode',
            field=models.IntegerField(default=0, choices=[(0, b'Cooling/Humidity Control'), (1, b'Humidity Control'), (5, b'Heating'), (9, b'Off')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='program',
            name='temperature',
            field=models.IntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='setting',
            name='humidity',
            field=models.IntegerField(default=55),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='setting',
            name='mode',
            field=models.IntegerField(default=0, choices=[(0, b'Cooling'), (1, b'Humidity Control'), (5, b'Heating'), (9, b'Off')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='setting',
            name='source',
            field=models.IntegerField(default=0, verbose_name=b'source of last change', choices=[(0, b'Climaduino'), (1, b'Controller'), (3, b'Program')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='setting',
            name='temperature',
            field=models.IntegerField(default=77),
            preserve_default=True,
        ),
    ]
