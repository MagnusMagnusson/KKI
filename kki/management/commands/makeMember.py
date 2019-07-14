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
		parser.add_argument('ssn', nargs='+', type=str)
	@transaction.atomic
	def handle(self, *args, **options):
		ssn = options['ssn'][0]
		person = Person.objects.get(ssn = ssn)
		password = str(person.ssn)
		pword = auth.hash_password(password)
		member = Member()
		member.person = person
		member.password = pword[0]
		member.salt = pword[1]
		member.save()

