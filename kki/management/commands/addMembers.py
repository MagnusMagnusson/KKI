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
			spamreader = csv.reader(lengthfile, quotechar='"',delimiter = ";")
			Length = sum(1 for row in spamreader)
			print("Length recorded as " + str(Length))
		lengthfile.close()

		with open(options['File'][0], 'rt') as csvfile:
			
			spamreader = csv.reader(csvfile, quotechar='"',delimiter = ";")
			first = True
			print("loaded")
			done = 0
			lastpercent = 0.05
			for row in spamreader:
				person = Person()
				person.name = row[0]
				person.ssn = row[1]
				person.address = row[2]
				person.city = row[4]
				person.postcode = row[3]
				person.country = "ISL"
				person.email = row[5]
				person.comment = row[17]
				person.save()
				member = Member()
				member.person = person;
				member.payer = None;
				password = person.ssn
				pword = auth.hash_password(password)
				member.password = pword[0]
				member.salt = pword[1]
				member.save()
				years = [18,22,25]
				for year in years:
					if(row[year] != ""):
						dateTime = datetime.strptime(row[year],"%d.%m.%Y")
						paymentDate = dateTime.date()
						p = Payment()
						p.date = paymentDate
						p.member = member
						p.save()
				done += 1
				if(float(done/Length) >= lastpercent):
					lastpercent += 0.05
					print(str(float(100*done/Length)) + "% done")
						

		csvfile.close()
