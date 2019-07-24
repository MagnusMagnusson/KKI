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
	def add_arguments(self, parser):
		parser.add_argument('File', nargs='+', type=str)
	@transaction.atomic
	def handle(self, *args, **options):
		print("started better")
		Length = 1
		with open(options['File'][0], 'rt') as lengthfile:
			spamreader = csv.reader(lengthfile, quotechar='"',delimiter = ",")
			Length = sum(1 for row in spamreader)
			print("Length recorded as " + str(Length))
		lengthfile.close()

		with open(options['File'][0], 'rt') as csvfile:
			
			spamreader = csv.reader(csvfile, quotechar='"',delimiter = ",")
			first = True
			print("loaded")
			done = 0
			lastpercent = 0.05
			for row in spamreader:
				print(row)
				award = Award()
				award.name = row[0]
				award.save()
		csvfile.close()
