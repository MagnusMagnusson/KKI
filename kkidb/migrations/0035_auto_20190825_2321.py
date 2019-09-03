# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-08-25 23:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kkidb', '0034_auto_20190729_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catcert',
            name='judgement',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='kkidb.Judgement'),
        ),
        migrations.AlterField(
            model_name='judgement',
            name='abs',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='judgement',
            name='biv',
            field=models.BooleanField(default=False),
        ),
    ]
