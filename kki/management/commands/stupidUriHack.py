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
from kkidb.models import Payment
import random

class Command(BaseCommand):
	@transaction.atomic
	def handle(self, *args, **options):
		payments = Payment.objects.all()
		for p in payments:
			p.uri = "".join(random.choice("qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM1234567890") for _ in range(6))
			p.save()
