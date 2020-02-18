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
		print("creating permissions")
		perms = [
		"person_get",
		"person_patch",
		"person_post",
		"person_delete",
		"member_get",
		"member_patch",
		"member_post",
		"member_delete",
		"organization_get",
		"organization_patch",
		"organization_post",
		"organization_delete",
		"cat_get",
		"cat_patch",
		"cat_post",
		"cat_delete",
		"show_get",
		"show_patch",
		"show_post",
		"show_delete",
		"showrunner_get",
		"showrunner_patch",
		"showrunner_delete",
		"showrunner_post",
		"account_management",
		]
		for perm in perms:
			if Permission.objects.filter(name = perm).count() == 0:
				p = Permission()
				p.name = perm
				p.save()
				print("permission '"+p.name + "' saved")
			else:
				print("FAILED: permission '"+perm+"' already exists")
		print("creating groups")
		groups = {
			"sýningaritari":[
				"cat_get",
				"showrunner_get",
				"showrunner_patch",
				"showrunner_delete",
				"showrunner_post",
			],
			"skráningastjóri":[		
				"person_get",
				"person_patch",
				"person_post",
				"person_delete",
				"member_get",
				"member_patch",
				"member_post",
				"member_delete",
				"organization_get",
				"organization_patch",
				"organization_post",
				"organization_delete",
				"cat_get",
				"cat_patch",
				"cat_post",
				"cat_delete",
				"show_get",
				"show_patch",
				"show_post",
				"show_delete",
				"showrunner_get",
				"showrunner_patch",
				"showrunner_delete",
				"showrunner_post",
		],
			"stjórn":[				
				"person_get",
				"person_patch",
				"person_post",
				"person_delete",
				"member_get",
				"member_patch",
				"member_post",
				"member_delete",
				"organization_get",
				"organization_patch",
				"organization_post",
				"organization_delete",
				"cat_get",
				"show_get",
				], #Stofnanir + félagar
			"félagi":[
			"cat_get",
			"show_get"
			],
		    "kerfisstjórn":[
				"person_get",
				"person_patch",
				"person_post",
				"person_delete",
				"member_get",
				"member_patch",
				"member_post",
				"member_delete",
				"organization_get",
				"organization_patch",
				"organization_post",
				"organization_delete",
				"cat_get",
				"cat_patch",
				"cat_post",
				"cat_delete",
				"show_get",
				"show_patch",
				"show_post",
				"show_delete",
				"showrunner_get",
				"showrunner_patch",
				"showrunner_delete",
				"showrunner_post",
				"account_management",	
			]#sAlgangur
		}

		for group in groups:
			if(UserGroup.objects.filter(name = group).count() == 0):
				perms = groups[group]
				g = UserGroup()
				g.name = group
				g.save()
				print("Group '"+g.name+"' created")
				for perm in perms:
					p = Permission.objects.get(name = perm)
					gp = GroupPermission()
					gp.group = g 
					gp.permission = p
					gp.save()
			else:
				print("Error: Group " +group+" already exists")
