# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-29 12:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kkidb', '0032_auto_20190728_2029'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='public',
            field=models.BooleanField(default=True),
        ),
    ]
