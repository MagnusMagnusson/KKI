# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import random


class Person(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 75, null = True)
	ssn = models.CharField(max_length = 10, null = True)
	address = models.CharField(max_length = 50, null = True)
	city = models.CharField(max_length = 50, null = True)
	postcode = models.CharField(max_length = 10, null = True)
	country = models.CharField(max_length = 3, null = True)
	phoneNumber = models.CharField(max_length = 25, null = True)
	comment = models.CharField(max_length = 2048, null = True)
	email = models.CharField(max_length=1024,null = True)

class Member(models.Model):
	id = models.CharField(primary_key=True, max_length=6)
	person = models.OneToOneField('Person', on_delete=models.CASCADE)
	payer = models.ForeignKey('Member',null=True)
	salt = models.CharField(max_length=256)
	password = models.CharField(max_length = 256)

	def save(self):
		if(not self.id):
			i = random.randrange(000000,999999)
			i = str(i).zfill(6)
			print(i)
			print("yo")
			self.id = i
		super(Member, self).save()

class Payment(models.Model):
	date = models.DateField()
	member = models.ForeignKey(Member)
	giftYear = models.BooleanField(default=False)
	comment = models.CharField(max_length = 1024, null = True)

class Owner(models.Model):
	person = models.ForeignKey('Person')
	cat = models.ForeignKey('Cat')
	date = models.DateField(null=True)
	current = models.BooleanField()

class Judge(models.Model):
	person = models.ForeignKey('Person')

class Cattery(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 50)
	country = models.CharField(max_length = 3, null=True)
	prefix = models.BooleanField()
	organization = models.ForeignKey("Organization",null = True)

class CatteryOwner(models.Model):
	cattery = models.ForeignKey('Cattery')
	owner = models.OneToOneField('Person')

class Cat(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 50)
	reg_full = models.CharField(max_length = 50, null = True)
	birth_date = models.DateField(null = True)
	reg_date = models.DateField(null = True)
	gender = models.BooleanField()
	dam = models.ForeignKey('Cat',related_name='dam_children',null=True)
	sire = models.ForeignKey('Cat',related_name='sire_children', null=True)
	cattery = models.ForeignKey('Cattery',null=True)

class Import(models.Model):
	cat = models.OneToOneField('Cat')
	organization = models.ForeignKey('organization')
	country = models.CharField(max_length = 3)
	original_reg_date = models.DateField()
	original_reg_id = models.CharField(max_length = 20)

class Neuter(models.Model):
	cat = models.OneToOneField('Cat', primary_key = True)
	date = models.DateField()

class Microchip(models.Model):
	id = models.AutoField(primary_key = True)
	cat = models.ForeignKey('Cat')
	microchip = models.CharField(max_length = 30)

class Organization(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 50)
	country = models.CharField(max_length = 3)

class Breed(models.Model):
	breed = models.CharField(max_length = 25)
	category = models.IntegerField()
	short = models.CharField(max_length = 5)

class Color(models.Model):
	color = models.CharField(max_length=50)
	short = models.CharField(max_length=20)
	desc = models.CharField(max_length=1024)

class EMS(models.Model):
	cat = models.ForeignKey('Cat')
	breed = models.ForeignKey('Breed')
	color = models.ForeignKey('Color')
	date = models.DateField()

############# Shows

class Show(models.Model):
	name = models.CharField(max_length = 51)
	orginizer = models.ForeignKey('Person')
	date = models.DateField()
	location = models.CharField(max_length = 50)

class Entry(models.Model):
	cat = models.ForeignKey('Cat')
	show = models.ForeignKey('Show')
	catalog_nr = models.IntegerField()
	guest = models.BooleanField() 	
	class Meta:
		unique_together = ('show', 'cat')
		unique_together = ('show', 'catalog_nr')

class ShowJudges(models.Model):
	show = models.ForeignKey(Show)
	judge = models.ForeignKey(Judge)
	class Meta:
		unique_together = ('show','judge')

class Judgement(models.Model):
	entry = models.OneToOneField('Entry', primary_key = True)
	judge = models.ForeignKey('Judge')
	judgement = models.CharField(max_length = 10) #EX1
	biv = models.BooleanField()
	abs = models.BooleanField()
	comment = models.CharField(max_length = 2048)

class Litter(models.Model):
	class Meta:
		unique_together = ('show', 'catalog')
	catalog = models.CharField(max_length = 3)
	show = models.ForeignKey('Show')

class LitterCat(models.Model):
	litter = models.ForeignKey('Litter')
	entry = models.OneToOneField('Entry', primary_key = True)

class LitterJudgement(models.Model):
	show = models.ForeignKey('Show')
	judge = models.ForeignKey('Judge')
	abs = models.BooleanField()
	rank = models.IntegerField()
	comment = models.CharField(max_length = 2048)
	litter = models.ForeignKey('Litter')

class Cert(models.Model):
	certName = models.CharField(max_length = 10)
	certRank = models.IntegerField()
	next = models.ForeignKey('Cert')
	neuter = models.BooleanField()

class CatCert(models.Model):
	cat = models.ForeignKey('Cat')
	judge = models.ForeignKey('Judgement')
	cert = models.ForeignKey('Cert')
	ems = models.CharField(max_length = 20)

class Title(models.Model):
	name = models.CharField(max_length = 50)
	short = models.CharField(max_length = 10)
	cert = models.ForeignKey('Cert')

class Nomination(models.Model):
	judgement = models.ForeignKey('Judgement')
	award = models.ForeignKey('Award')
	bis = models.BooleanField()

class LitterNomination(models.Model):
	judgement = models.ForeignKey('LitterJudgement')
	award = models.ForeignKey('Award')

class Award(models.Model):
	name = models.CharField(max_length = 50)




	#Auth

class Permissions(models.Model):
	id = models.BigIntegerField(primary_key = True)
	name = models.CharField(max_length=20, unique = True)

class MemberPermissions(models.Model):
	user = models.ForeignKey(Member)
	permission = models.ForeignKey(Permissions)
	class Meta:
		unique_together = (('user', 'permission'))

class Login_log(models.Model):
	id = models.AutoField(primary_key = True)
	user = models.ForeignKey(Member)
	time = models.DateTimeField()
	lastRefresh = models.DateTimeField(null = True)
	expires = models.BooleanField(default = True)
	ip = models.CharField(max_length = 50)
	cookie = models.CharField(max_length = 256, unique = True, null = True)