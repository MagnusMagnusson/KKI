from django.core.management.base import BaseCommand, CommandError
from kkidb.models import *
import sys
from  kkidb.auth import auth
import random

class Command(BaseCommand):	
	def add_arguments(self, parser):
		parser.add_argument('ssn', nargs='+', type=str)
		parser.add_argument('password', nargs='+', type=str)

	def handle(self, *args, **options):
		ssn = options['ssn'][0]
		pWord = options['password'][0]
		
		person = Person.objects.get(ssn=ssn)
		member = person.member
		password = auth.hash_password(pWord)
		member.password = password[0]
		member.salt = password[1]
		member.save()
