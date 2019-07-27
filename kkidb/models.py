# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import random


class Person(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 75)
	ssn = models.CharField(max_length = 10, null = True, unique = True)
	address = models.CharField(max_length = 50, null = True)
	city = models.CharField(max_length = 50, null = True)
	postcode = models.CharField(max_length = 10, null = True)
	country = models.CharField(max_length = 3, null = True)
	phoneNumber = models.CharField(max_length = 25, null = True)
	comment = models.CharField(max_length = 2048, null = True)
	email = models.CharField(max_length=1024,null = True)

	def fullAddress(self):
		str = self.address
		if self.city:
			str += ", " + self.city
		if self.postcode:
			str += " ("+self.postcode+")"
		return str

	def toObject(self):
		member = {}
		member['name'] = self.name.encode('utf-8')
		member['ssn'] = self.ssn
		member['email'] = self.email
		member['address'] = self.address
		member['postcode'] = self.postcode
		member['city'] = self.city
		member['pid'] = self.id
		if(hasattr(self, 'member')):
			member['last_payment'] = self.member.lastPaymentDate() if self.member else None 
			member['id'] = self.member.id if self.member else None
		return member

class Member(models.Model):
	id = models.CharField(primary_key=True, max_length=6)
	person = models.OneToOneField('Person', on_delete=models.CASCADE)
	salt = models.CharField(max_length=256)
	password = models.CharField(max_length = 256)

	def allPayments(self):
		payment_set = self.memberpayment_set;
		payments = []
		for payment in payment_set.all().order_by('-payment__date'):
			payments.append(payment.payment)
		return payments

	def lastPaymentDate(self):
		payments = self.allPayments()
		if(len(payments) > 0):
			return payments[0].date
		return None;

	def lastPayment(self):
		payments = self.allPayments()
		if(len(payments) > 0):
			return payments[0]
		return None;

	def firstPaymentDate(self):
		payments = self.allPayments()
		if(len(payments) > 0):
			return payments[len(payments)-1].date
		return None;

	def toObject(self):
		return self.person.toObject()
	
	def save(self):
		if(not self.id):
			i = random.randrange(000000,999999)
			i = str(i).zfill(6)
			self.id = i
		super(Member, self).save()

class Payment(models.Model):
	date = models.DateField()
	giftYear = models.BooleanField(default=False)
	comment = models.CharField(max_length = 1024, null = True)
	method = models.CharField(max_length=128)
	payer = models.ForeignKey(Member, related_name='payer', null=True, on_delete=models.CASCADE)

	def updateMembers(self, newMembers):
		currentMembers = self.memberEntries()
		currentMemberInstances = []
		deleted = 0
		added = 0
		new = 0
		for mp in currentMembers:
			currentMemberInstances.append(mp.member)
		#delete all currently attached members that are not in the new set
		for entry in currentMembers:
			m = entry.member.person
			if not m in newMembers:
				m.delete()
				delted += 1
		#add all members not currently attatched, creating memberships for those that do not have it
		for person in newMembers:
			if person.member is None:
				newMember = Member()
				newMember.person = person
				newMember.password = ""
				newMember.salt = ""
				newMember.save()
				new += 1
			if(person.member not in currentMemberInstances):
				mp = MemberPayment()
				mp.payment = self
				mp.member = person.member
				mp.save()
				added += 1
		return (added,deleted,new)
				
	def memberEntries(self):
		mpset = self.memberpayment_set.all()
		return mpset

	def members(self):
		mpset = self.memberpayment_set
		members = []
		for mp in mpset.all():
			members.append(mp.member.person)
		return members

class MemberPayment(models.Model):
	member = models.ForeignKey(Member, on_delete=models.CASCADE)
	payment = models.ForeignKey(Payment)
	class Meta:
		unique_together = ("member","payment")

class Owner(models.Model):
	person = models.ForeignKey('Person')
	cat = models.ForeignKey('Cat')
	date = models.DateField(null=True)
	current = models.BooleanField()

	def toObject(self):
		owner = {}
		owner['person'] = self.person.toObject()
		owner['cat'] = self.cat.toObject()
		owner['date'] = self.date
		owner['current'] = self.current 
		return owner

class Judge(models.Model):
	person = models.OneToOneField('Person')

class Cattery(models.Model):
	id = models.AutoField(primary_key = True)
	registry_date = models.DateField(null = True)
	name = models.CharField(max_length = 50, unique=True)
	country = models.CharField(max_length = 3, null=True)
	prefix = models.BooleanField()
	organization = models.ForeignKey("Organization",null = True)
	email = models.CharField(max_length=1024,null=True)
	address = models.CharField(max_length = 50, null = True)
	city = models.CharField(max_length = 50, null = True)
	postcode = models.CharField(max_length = 10, null = True)
	website = models.CharField(max_length = 1024, null = True)
	phone = models.CharField(max_length = 50, null = True)

	def toObject(self):
		cattery = {}
		cattery['id'] = self.id
		cattery['name'] = self.name
		cattery['country'] = self.country
		if self.organization:
			cattery['organization'] = self.organization.name
		else:
			cattery['organization'] = None
		cattery['email'] = self.email
		cattery['address'] = self.address
		cattery['postcode'] = self.postcode
		cattery['city'] = self.city
		cattery['website'] = self.website
		cattery['phone'] = self.phone
		cattery['owners'] = []
		for person in self.catteryowner_set.all():
			cattery['owners'].append(person.owner.toObject())
		return cattery 

	def memberEntries(self):
		mpset = self.catteryowner_set.all()
		return mpset

	def updateMembers(self, newMembers):
		currentMembers = self.memberEntries()
		currentMemberInstances = []
		deleted = 0
		added = 0
		new = 0
		for mp in currentMembers:
			currentMemberInstances.append(mp.owner)
		#delete all currently attached members that are not in the new set
		for entry in currentMembers:
			m = entry.owner
			if not m in newMembers:
				entry.delete()
				deleted += 1
		#add all members not currently attatched
		for person in newMembers:
			if(person not in currentMemberInstances):
				mp = CatteryOwner()
				mp.cattery = self
				mp.owner = person
				mp.save()
				added += 1
		return (added,deleted,new)

	def fullAddress(self):
		str = self.address
		if self.city:
			str += ", " + self.city
		if self.postcode:
			str += " ("+self.postcode+")"
		return str

class CatteryOwner(models.Model):
	cattery = models.ForeignKey('Cattery')
	owner = models.OneToOneField('Person')

class Cat(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 50)
	reg_full = models.CharField(max_length = 50, null = True, unique=True)
	reg_nr = models.IntegerField(null = True)
	birth_date = models.DateField(null = True)
	reg_date = models.DateField(null = True)
	isMale = models.BooleanField()
	dam = models.ForeignKey('Cat',related_name='dam_children',null=True)
	sire = models.ForeignKey('Cat',related_name='sire_children', null=True)
	cattery = models.ForeignKey('Cattery',null=True)


	def owners(self):
		ownerset = self.owner_set.all().filter(current = True)
		return ownerset

	def ownerHistory(self):
		ownerset = self.owner_set.all()
		return ownerset

	def groupedOwnerHistory(self):
		owners = self.ownerHistory().order_by('date')
		dates = {}
		for owner in owners:
			if owner.date not in dates:
				dates[owner.date] = []
			dates[owner.date].append(owner)
		return dates

	def fullName(self):
		t1 = self.highestTitle(False)
		t2 = self.highestTitle(True)
		s = ""
		if t1:
			if t2:
				s += t1.short + ", " + t2.short + " "
			else:
				s += t1.short + " "
		elif t2:
			s += t2.short + " "
		s += self.name
		return s


	def allEms(self):
		ems_set = self.catems_set;
		ems_list = []
		for ems in ems_set.all().order_by('-date'):
			ems_list.append(ems)
		return ems_list

	def ems(self):
		emss = self.allEms()
		if len(emss) > 0:
			return emss[0]

	def highestCert(self,neutered = False):
		catSet = self.catcert_set.all().filter(cert__neuter = neutered)
		if len(catSet) > 0:
			catSet = list(catSet)
			def absSort(a):
				return a.absRank() 
			catSet.sort(key=absSort)
			return catSet[0]
		else:
			return None

	def highestTitle(self,neutered = False):
		cert = self.highestCert(neutered)
		if cert:
			return cert.cert.getTitle()
		else:
			return None

	def updateOwners(self, owners, date):
		currentOwners = self.owners()
		currentOwnerInstances = []
		deleted = 0
		added = 0
		new = 0
		for co in currentOwners:
			currentOwnerInstances.append(co.person)
		#delete all currently attached members that are not in the new set
		for entry in currentOwners:
			m = entry.person
			if not m in owners:
				entry.current = False
				entry.save()
				deleted += 1
		#add all members not currently attatched
		for person in owners:
			if(person not in currentOwnerInstances):
				ow = Owner()
				ow.cat = self
				ow.person = person
				ow.current = True
				ow.date = date
				ow.save()
				added += 1
		return (added,deleted,new)

	#Returns all siblings that were born in the same litter as self
	def litterMates(self):
		if self.sire is None or self.dam is None:
			return Cat.objects.none()
		Q = Cat.objects.filter(sire = self.sire,dam = self.dam, birth_date = self.birth_date).exclude(id = self.id)
		return Q

	#Returns all siblings have both the same father and mother, with the option of excluding littermates
	def fullSiblings(self, excludeLitterMates = True):
		if self.dam is None or self.sire is None:
			return Cat.objects.none()
		Q = Cat.objects.filter(sire = self.sire, dam = self.dam).exclude(sire = None).exclude(dam = None)
		if excludeLitterMates:
			Q = Q.exclude(birth_date = self.birth_date)
		return Q 

	#Returns all siblings that only share a mother, but not father. 
	def maternalSiblings(self):
		if self.dam is None:
			return Cat.objects.none()
		Q = Cat.objects.filter(dam = self.dam).exclude(sire = self.sire).exclude(dam = None).exclude(id = self.id)
		return Q

	def paternalSiblings(self):
		if self.sire is None:
			return Cat.objects.none()
		Q = Cat.objects.filter(sire = self.sire).exclude(dam = self.dam).exclude(sire = None).exclude(id = self.id)
		return Q

	#Returns all siblings.
	def siblings(self):
		Q = Cat.objects.filter(sire = self.sire).exclude(sire = None).exclude(id = self.id) | Cat.objects.filter(dam = self.dam).exclude(dam = None).exclude(id = self.id)
		return Q

	def children(self):
		Q = Cat.objects.filter(sire = self) | Cat.objects.filter(dam = self)
		return Q

	def litters(self):
		Q = self.children()
		Q.order_by("-birth_date","sire","dam")
		litters = []
		l = None
		s = None 
		d = None
		for cat in Q:
			if cat.birth_date != l or cat.sire != s or cat.dam != d:
				l = cat.birth_date
				s = cat.sire 
				d = cat.dam 
				litters.append((l,[]))
			litters[len(litters) - 1][1].append(cat) 
		def sortFunc(a,b = None):
			if b is None:
				return 0 
			if a[0] < b[0]:
				return -1
			if a[0] == b[0]:
				return 0
			return 1

		litters.sort()
		return litters

	def children(self):
		Q = Cat.objects.filter(sire = self) | Cat.objects.filter(dam = self)
		return Q

	def toObject(self):
		cat = {} 
		cat['id'] = self.id 
		if self.ems():
			cat['ems'] = str(self.ems().ems)
		else:
			cat['ems'] = None
		cat['name'] = self.name
		cat['fullName'] = self.fullName()
		cat['registry'] = self.reg_full
		cat['birthdate'] = self.birth_date
		cat['regdate'] = self.reg_date
		cat['gender'] = "Male" if self.isMale else "Female"
		cat['owners'] = []
		for owner in self.owners():
			cat['owners'].append(owner.person.toObject())
		if self.cattery:
			cat['cattery'] = self.cattery.toObject()
		else:
			cat['cattery'] = None
		return cat




class Import(models.Model):
	cat = models.OneToOneField('Cat')
	organization = models.ForeignKey('organization')
	country = models.CharField(max_length = 3)
	original_reg_date = models.DateField()
	original_reg_id = models.CharField(max_length = 20)

class Neuter(models.Model):
	cat = models.OneToOneField('Cat', primary_key = True)
	date = models.DateField(null = True)

class Microchip(models.Model):
	id = models.AutoField(primary_key = True)
	cat = models.ForeignKey('Cat')
	microchip = models.CharField(max_length = 30)

class Organization(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 100)
	short = models.CharField(max_length = 15, null=True)
	country = models.CharField(max_length = 3)

class Breed(models.Model):
	breed = models.CharField(max_length = 25, unique=True)
	category = models.IntegerField()
	short = models.CharField(max_length = 5,unique = True)

class Color(models.Model):
	color = models.CharField(max_length=50, unique = True)
	short = models.CharField(max_length=20, unique = True)
	desc = models.CharField(max_length=1024)

class EMS(models.Model):
	breed = models.ForeignKey('Breed')
	color = models.ForeignKey('Color')
	group = models.IntegerField(null = True)
	
	def toObject(self):
		ems = {}
		ems['ems'] = str(self)
		return ems
	
	def __str__(self):
		return self.breed.short + " " + self.color.short
	
	class Meta:
		unique_together = ('breed', 'color')

class CatEms(models.Model):
	cat = models.ForeignKey('Cat')
	ems = models.ForeignKey('EMS')
	date = models.DateField()
	def __str__(self):
		return str(self.ems)
	def toObject(self):
		ems = {}
		ems['cat'] = self.cat.id
		ems['date'] = self.date 
		ems['ems'] = self.ems.toObject()
		return ems

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

	def date(self):
		return self.entry.show.date

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
	name = models.CharField(max_length = 10)
	rank = models.IntegerField()
	next = models.ForeignKey('Cert', null=True)
	neuter = models.BooleanField()

	def prev(self):
		certQ = Cert.objects.filter(next = self).exclude(id = self.id)
		if len(certQ) == 0:
			return None
		else:
			return certQ[0]
			

	def getTitle(self):
		if hasattr(self,'title'):
			return self.title
		else:
			if self.prev():
				return self.prev().getTitle()
			else:
				return None

	def absRank(self):
		if(self.next):
			if self.next == self:
				return 1
			else:
				return 1 + self.next.absRank()
		else:
			return 1

class CatCert(models.Model):
	cat = models.ForeignKey('Cat')
	judgement = models.ForeignKey('Judgement', null=True)
	cert = models.ForeignKey('Cert')
	ems = models.CharField(max_length = 20, null=True)

	def title(self):
		return self.cert.title()

	def absRank(self):
		return self.cert.absRank()


class Title(models.Model):
	name = models.CharField(max_length = 50)
	short = models.CharField(max_length = 10)
	cert = models.OneToOneField('Cert',null=True)

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