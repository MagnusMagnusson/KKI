# -*- coding: utf-8 -*-
import csv
import os
from django.core.management.base import BaseCommand, CommandError
from kkidb.models import *
from django.utils import timezone
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from datetime import date
from kkidb.auth import auth
from django.db import transaction

class Command(BaseCommand):
	@transaction.atomic
	def handle(self, *args, **options):
		a = [98,99]
		for show_id in a:
			e = Entry.objects.filter(guest = True, show_id = show_id)
			for cat in e:
				cat.guest = False 
				cat.save()
		
