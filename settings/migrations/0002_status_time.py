# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 3, 13, 45, 12, 527964, tzinfo=utc), verbose_name=b'last change'),
            preserve_default=False,
        ),
    ]
