# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-05 19:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kkidb', '0015_cattery_website'),
    ]

    operations = [
        migrations.AddField(
            model_name='cattery',
            name='phone',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
