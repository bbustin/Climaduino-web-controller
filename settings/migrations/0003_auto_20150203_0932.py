# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0002_status_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='setting',
            name='currentlyRunning',
        ),
        migrations.RemoveField(
            model_name='setting',
            name='stateChangeAllowed',
        ),
    ]
