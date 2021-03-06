# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-05 18:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kkidb', '0013_auto_20190701_0040'),
    ]

    operations = [
        migrations.AddField(
            model_name='cattery',
            name='address',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='cattery',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='cattery',
            name='email',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='cattery',
            name='postcode',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
