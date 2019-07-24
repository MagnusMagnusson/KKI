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
import json

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('File', nargs='+', type=str)
	@transaction.atomic
	def handle(self, *args, **options):
		file = options['File'][0]
		print("Starting pre-import")
		with open(file, 'r') as f:
			dataStore = json.load(f)
		done = 0.0
		lastPerc = 0.05
		length = len(dataStore)
		print("Loaded a datastore of length " + str(length))
		print("Starting seperation into in-memory DB")
		db = {}

		for item in dataStore:
			done += 1
			if ((100*done)/length) > lastPerc:
				#print(str(lastPerc) + "% imported")
				lastPerc += 0.05
			model = item['model'].split(".")[1]
			if model not in db:
				db[model] = []
				#print(model)
			item['fields']['pk'] = item['pk']
			db[model].append(item['fields'])
		
		kkidb['ems'] = {}

		for ems in db['ems']:
			_breed = ems['breed']
			_color = ems['ems']
			_category = ems['category']
			_group = ems['group']

			breedQ = Breed.objects.filter(breed = _breed)
			if(len(breedQ) > 0):
				breed = breedQ[0]
			else: 
				continue

			
			colorQ = Color.objects.filter(color = _color)
			if(len(colorQ) > 0):
				color = colorQ[0]
			else:
				continue

			emsCheck = EMS.objects.filter(breed = breed, color = color)
			if(len(emsCheck) > 0):
				kkidb['ems'][ems['pk']] = emsCheck[0]
			

