# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-29 01:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kkidb', '0008_payment_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='payer',
        ),
        migrations.AddField(
            model_name='payment',
            name='payer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payer', to='kkidb.Member'),
        ),
    ]
