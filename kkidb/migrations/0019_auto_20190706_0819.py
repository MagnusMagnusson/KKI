# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-06 08:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kkidb', '0018_organization_short'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='short',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
