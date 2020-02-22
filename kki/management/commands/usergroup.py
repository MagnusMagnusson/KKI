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
	def add_arguments(self, parser):
		
		parser.add_argument('command',  type=str)
		parser.add_argument(
            '-u',
            help='Specifies the email of the account',
        )        
		parser.add_argument(
            '-g',
            help='Specifies the group in question',
        )

	def handle(self, *args, **options):
		comm = options['command']
		if comm == "members":
			if options['g']:
				try:
					group = UserGroup.objects.get(name = options['g'])
					print("There are " + str(len(group.groupmember_set.all())) + " users in '"+options['g']+"'")
					for a in group.groupmember_set.all():
						print(a.account.email + " - " + str(a.account.active))
				except group.DoesNotExist as ex:
					print("The group '"+options['g']+"' does not exist")
			else:
				print("Missing parameter -g for the group indicated")
		elif comm == "add":
			if options['u']:
				if options['g']:
					try:
						group = UserGroup.objects.get(name = options['g'])
						account = Account.objects.get(email = options['u'])
						gm = GroupMember()
						gm.group = group
						gm.account = account
						gm.save()
						print("User account with email '"+options['g']+"' added to group '"+options['u']+"'")
					except UserGroup.DoesNotExist as ex:
						print("The group '"+options['g']+"' does not exist")
					except Account.DoesNotExist as ex:
						print("The user email '"+options['u']+"' does not exist")
				else:
					print("Missing parameter -g for the group indicated")
			else:
				print("Missing parameter -u for the user account indicated")
		elif comm == "remove":
			if options['u']:
				if options['g']:
					try:
						gm = GroupMember.objects.get(account__email = options['u'], group__name = options['g'])
						gm.delete()
						print("Member removed from group")
					except GroupMember.DoesNotExist as ex:
						print("The indicated member doesn't belong to the group")
				else:
					print("Missing parameter -g for the group indicated")
			else:
				print("Missing parameter -u for the user account indicated")

