# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import random
import uuid
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import date,datetime

cache = {}

def getCache(model,id,var):
	key = hash(str(model) + "-"+ str(id) + "-"+ str(var))
	if key in cache:
		return cache[key]
	return None

def setCache(model,id,var,value):	
	key = hash(str(model) + "-"+ str(id) + "-"+ str(var))
	cache[key] = value

def Randstring(n = 6):
	return  uuid.uuid4().hex[0:n]

#########People 
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
	@staticmethod
	def apiMap( filters):
		keyMapping = {
			"name":"name",
			"ssn":"ssn",
			"is_member":"member__isnull",
			"email":"email",
			"address":"address",
			"postcode":"postcode",
			"city":"city",
			"country":"country",
			"phone":"phoneNumber",
			"email":"email",
			"is_judge":"judge__isnull",
		}
		translatedFilter = {}
		for key in filters.keys():
			value = filters[key]
			if key in keyMapping:
				truekey = keyMapping[key]
				translatedFilter[truekey] = value
		if "member" in translatedFilter:
			translatedFilter["member"] = not translatedFilter["member"]
		if "judge" in translatedFilter:
			translatedFilter["judge"] = not translatedFilter["judge"]
	
		return translatedFilter
	def toObject(self):
		member = {}
		member['name'] = self.name
		member['ssn'] = self.ssn
		member['email'] = self.email
		member['address'] = self.address
		member['postcode'] = self.postcode
		member['city'] = self.city
		member['country'] = self.country
		member['id'] = self.id
		if(hasattr(self, 'member')):
			member['is_member'] = True
			member['last_payment'] = self.member.lastPaymentDate() 
			member['member_id'] = self.member.id 
		else:
			member['is_member'] = False
			
		if(hasattr(self, 'judge')):
			member['is_judge'] = True
			member['judge_id'] = self.judge.id
		else:
			member['is_judge'] = False
		return member
	@staticmethod 
	def create( resourceDict, id = None):
		person = Person()
		if id:
			person.id = id 
		person.name = "N/A"
		person.save()
		person.patch(resourceDict)
		return person 
	def patch(self, resourceDict):
		if "name" in resourceDict:
			self.name = resourceDict["name"]
		if "ssn" in resourceDict:
			self.ssn = resourceDict["ssn"]
		if "email" in resourceDict:
			self.email = resourceDict["email"]
		if "address" in resourceDict:
			self.address = resourceDict["address"]
		if "postcode" in resourceDict:
			self.postcode = resourceDict["postcode"]
		if "city" in resourceDict:
			self.city = resourceDict["city"]
		if "country" in resourceDict:
			self.country = resourceDict["country"]
		if "is_member" in resourceDict:
			if resourceDict["is_member"] == True:
				if not hasattr(self,"member"):
					membership = Member()
					membership.person = self
					membership.salt = "NOT SET"
					membership.password = "NOT SET"
					membership.save()
			elif resourceDict["is_member"] == False:
				if hasattr(self,"member"):
					self.member.delete()
		if "is_judge" in resourceDict:
			if resourceDict["is_judge"] == True:
				if not hasattr(self,"judge"):
					judgeship = Judge()
					judgeship.person = self
					judgeship.save()
			elif resourceDict["is_judge"] == False:
				if hasattr(self,"judge"):
					self.member.delete()
		self.save()
class Member(models.Model):
	id = models.CharField(primary_key=True, max_length=6)
	person = models.OneToOneField('Person', on_delete=models.CASCADE)
	salt = models.CharField(max_length=256, default = "NOT SET")
	password = models.CharField(max_length = 256, default = "NOT SET")

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
	uri = models.CharField(max_length = 6, null = False, unique= True, default = Randstring)

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
				newMember.password = "NOT SET"
				newMember.salt = "NOT SET"
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

	def toObject(self):
		p = {}
		p['date'] = self.date 
		p['method'] = self.method 
		p['comment'] = self.comment 
		p['id'] = self.uri
		p['is_giftyear'] = self.giftYear
		if self.payer:
			p['payer'] = self.payer.id
		else:
			p['payer'] = None
		p['beneficieries'] = []
		for mem in self.members():
			p['beneficieries'].append(mem.member.id)
		return p

	def patch(self, data):
		if "date" in data:
			self.date = data["date"]
		if "is_giftYear" in data:
			self.giftYear = data["is_giftYear"]
		if "comment" in data:
			self.comment = data["comment"]
		if "payer" in data:
			self.payer_id = data["payer"]
		if "method" in data:
			self.method = data["method"]
		if "beneficiary" in data:
			newMembers = []
			for id in data["beneficiary"]:
				m = Member.objects.get(id = id)
				newMembers.append(m.person)
			self.updateMembers(newMembers)
		self.save()
class MemberPayment(models.Model):
	member = models.ForeignKey(Member, on_delete=models.CASCADE)
	payment = models.ForeignKey(Payment,on_delete=models.CASCADE)
	class Meta:
		unique_together = ("member","payment")

	@staticmethod
	def apiMap(map):
		keyMapping = {
			"date":"payment__date",
			"is_giftYear":"payment__giftYear",
			"comment":"payment__comment",
			"payer":"payment__payer_id",
			"method":"payment__method",
			"beneficiary":"member_id",
			"beneficiary_name":"member__person__name",
		}
		translatedFilter = {}
		for key in filters.keys():
			value = filters[key]
			if key in keyMapping:
				truekey = keyMapping[key]
				translatedFilter[truekey] = value
	
		return translatedFilter
class Owner(models.Model):
	person = models.ForeignKey('Person',on_delete=models.CASCADE)
	cat = models.ForeignKey('Cat', on_delete=models.CASCADE)
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
	person = models.OneToOneField('Person',on_delete=models.CASCADE)
	def fullName(self):
		return self.person.name + " [ "+ self.person.country+" ]"

	def toObject(self):
		return self.person.toObject()
	
	def patch(self,rd):
		self.person.patch(rd)

	@staticmethod
	def apiMap(rd):
		map = Person.apiMap(rd)
		realMap = {}
		for key in map:
			realKey = "person__" + key
			realMap[realKey] = map[key]
		return realMap

	@staticmethod
	def create(rd,id = None):
		if "is_judge" in rd:
			rd['is_judge'] = False 
		per = Person.create(rd,None)
		try:
			j = Judge()
			j.id = id
			j.person = per
			j.save()
		except Exception:
			per.delete()
		return j
class Cattery(models.Model):
	id = models.AutoField(primary_key = True)
	registry_date = models.DateField(null = True)
	name = models.CharField(max_length = 50, unique=True)
	country = models.CharField(max_length = 3, null=True)
	prefix = models.BooleanField()
	organization = models.ForeignKey("Organization",null = True, on_delete=models.CASCADE)
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
		cattery['is_prefix'] = self.prefix
		if self.organization:
			cattery['organization'] = self.organization.name
		else:
			cattery['organization'] = None
		cattery['email'] = self.email
		cattery['address'] = self.address
		cattery['postcode'] = self.postcode
		cattery['city'] = self.city
		cattery['website'] = self.website
		cattery['phone_number'] = self.phone
		cattery['owners'] = []
		for person in self.catteryowner_set.all():
			cattery['owners'].append(person.owner.id)
		return cattery 

	def memberEntries(self):
		mpset = self.catteryowner_set.all()
		return mpset

	def updateMembers(self, newMembers):
		currentMembers = self.memberEntries()
		newMembers = [Person.objects.get(id = x) for x in newMembers]
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

	@staticmethod
	def apiMap(filters):
		keyMapping = {
			"name":"name",
			"registry_date":"registry_date",
			"country":"country",
			"is_prefix":"prefix",
			"organization":"organization",
			"email":"email",
			"address":"address",
			"city":"city",
			"postcode":"postcode",
			"website":"website",
			"phone_number":"phone",
			"owners": "catteryowner_set__owner__id"
		}
		translatedFilter = {}
		for key in filters.keys():
			value = filters[key]
			if key in keyMapping:
				truekey = keyMapping[key]
				translatedFilter[truekey] = value
		return translatedFilter

	@staticmethod 
	def create(resourceDict, id = None):
		cat = Cattery()
		if id:
			cat.id = id  
		cat.patch(resourceDict)
		return cat 

	def patch(self, resourceDict):
		rd = resourceDict
		if "name" in rd:
			self.name = rd["name"]
		if "registry_date" in rd:
			self.registry_date = rd["registry_date"]
		if "country" in rd:
			self.country = rd["country"]
		if "is_prefix" in rd:
			self.prefix = rd["is_prefix"]
		if "organization" in rd:
			self.organization_id = rd["organization"]
		if "email" in rd:
			self.email = rd['email']
		if "address" in rd:
			self.address = rd['address']
		if "city" in rd:
			self.city = rd['city']
		if "postcode" in rd:
			self.postcode = rd['postcode']
		if "website" in rd:
			self.website = rd['website']
		if "phone_number" in rd:
			self.phone = rd['phone_number']
		if "registry_date" in rd:
			self.registry_date = rd['registry_date']
		if "owners" in rd:
			self.save()
			self.updateMembers(rd['owners'])
		self.save()
class CatteryOwner(models.Model):
	cattery = models.ForeignKey('Cattery', on_delete=models.CASCADE)
	owner = models.OneToOneField('Person',on_delete=models.CASCADE)
class Organization(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 100)
	short = models.CharField(max_length = 15, null=True)
	country = models.CharField(max_length = 3)
	def toObject(self):
		o = {}
		o['id'] = self.id
		o['name'] = self.name
		o['acronym'] = self.short 
		o['country'] = self.country
		return o
	@staticmethod
	def apiMap( filters):
		keyMapping = {
			"id":"id",
			"name":"name",
			"acronym":"short",
			"country":"country"
		}
		translatedFilter = {}
		for key in filters.keys():
			value = filters[key]
			if key in keyMapping:
				truekey = keyMapping[key]
				translatedFilter[truekey] = value
		return translatedFilter
	@staticmethod 
	def create( resourceDict, id = None):
		org = Organization()
		if id:
			org.id = id 
		org.patch(resourceDict)
		return org 
	def patch(self, resourceDict):
		if "name" in resourceDict:
			self.name = resourceDict["name"]
		if "acronym" in resourceDict:
			self.short_name = resourceDict["acronym"]
		if "country" in resourceDict:
			self.country = resourceDict["country"]
		self.save()

######### Cats
class Cat(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 50)
	reg_full = models.CharField(max_length = 50, null = True, unique=True)
	reg_nr = models.IntegerField(null = True)
	registration_class = models.CharField(max_length = 3, null = True, default = "")
	country = models.CharField(max_length = 3, null = True, default = "")
	organization = models.ForeignKey("Organization", null=True, on_delete=models.PROTECT)
	birth_date = models.DateField(null = True)
	reg_date = models.DateField(null = True)
	isMale = models.BooleanField()
	dam = models.ForeignKey('Cat',related_name='dam_children',null=True, on_delete=models.PROTECT)
	sire = models.ForeignKey('Cat',related_name='sire_children', null=True,on_delete=models.PROTECT)
	cattery = models.ForeignKey('Cattery',null=True, on_delete=models.CASCADE)
	
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

	def microchip(self):
		chipset = self.microchip_set.all()
		if len(chipset) > 0:
			return chipset[len(chipset) - 1]
		else:
			return None

	def allEms(self):
		ems_set = self.catems_set;
		ems_list = []
		for ems in ems_set.all().order_by('-date'):
			ems_list.append(ems)
		return ems_list

	@property 
	def isNeutered(self):
		return hasattr(self,"neuter")

	def isKitten(self, _date = None):	
		if not _date:
			_date = date.today()
		kitten_cutoff = _date + relativedelta(months=-7)
		return self.birth_date >= kitten_cutoff

	def isJunior(self, d = None):
		if not d:
			d = date.today()
		youngling_cutoff = d + relativedelta(months=-10)
		return self.birth_date >= youngling_cutoff



	@property
	def division(self):
		g = "Male" if self.isMale else "Female"
		if self.isKitten():
			return g+" Kitten"
		elif self.isJunior():
			return g+ " Junior"
		else:
			e = self.ems
			cat = e.category if e else 0
			if cat == 5:
				return "Housecat " + g
			if hasattr(self,"neuter"):
				return "Cat."+  str(cat) + " neutered " + g
			else:
				return "Cat."+ str(cat) + " "+g

	@property
	def ems(self):
		emss = self.allEms()
		if len(emss) > 0:
			return emss[0]
		else:
			return None

	@ems.setter
	def ems(self,value):
		ems = EMS.getEMS(value)
		ce = CatEms()
		ce.ems = ems
		ce.cat = self 
		ce.date = date.today()
		ce.save()
		
	def highestCert(self,neutered = False):
		catSet = CatCert.objects.filter(cat = self, cert__neuter = neutered)
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
		id = str(self.id)
		#print(id + " 717 : " + str(datetime.now()) )
		cat = {} 
		cat['id'] = self.id 
		ems = self.ems
		#print(id + " 721 : " + str(datetime.now()) )
		if ems:
			cat['ems'] = str(ems.ems)
		else:
			cat['ems'] = None
		#print(id + " 726 : " + str(datetime.now()) )
		cat['name'] = self.name
		cat['full_name'] = self.fullName()
		
		#print(id + " 730 : " + str(datetime.now()) )
		cat['registry_number'] = self.reg_full
		cat['registry_digits'] = self.reg_nr
		cat['country'] = self.country
		cat['registration_class'] = self.registration_class
		cat['organization'] = self.organization
		
		#print(id + " 737 : " + str(datetime.now()) )
		cat['age_class'] = "Kitten" if self.isKitten() else "Junior" if self.isJunior() else "Adult"
		if ems:
			cat['category'] = ems.category
			cat['breed'] = ems.breed.breed
		else:
			cat['category'] = None 
			cat['breed'] = None
		
		#print(id + " 746 : " + str(datetime.now()) )
		cat['division'] = self.division
		
		#print(id + " 749 : " + str(datetime.now()) )

		cat['birthdate'] = self.birth_date
		cat['registration_date'] = self.reg_date
		cat['microchip'] = self.microchip()
		
		#print(id + " 755 : " + str(datetime.now()) )
		if cat['microchip']:
			cat['microchip'] = cat['microchip'].microchip
		
		#print(id + " 758 : " + str(datetime.now()) )
		cat['gender'] = "Male" if self.isMale else "Female"
		cat['owners'] = []
		
		#print(id + " 763 : " + str(datetime.now()) )
		for owner in self.owners():
			cat['owners'].append(owner.person_id)
		if self.cattery:
			cat['cattery'] = self.cattery_id
		else:
			cat['cattery'] = None
		
		#print(id + " 721 : " + str(datetime.now()) )
		cat['sire'] = self.sire_id 
		cat['dam'] = self.dam_id
		
		#print(id + " 775 : " + str(datetime.now()) )
		if hasattr(self,"neuter"):
			cat['neutered'] = True 
			cat['neutered_date'] = self.neuter.date
		else:
			cat['neutered'] = False 
			cat['neutered_date'] = None
		cat['dam'] = self.dam_id
		return cat

	@staticmethod
	def apiMap(filters):
		#print(filters)
		keyMapping = {
			"name":"name",
			"neutered":"neuter__isnull",
			"registry_number":"reg_full",
			"registry_digits":"reg_nr",
			"country":"country",
			"registration_class":"registration_class",
			"organization":"organization__name",
			"gender":"isMale",
			"cattery":"cattery__name",
		}
		translatedFilter = {}
		for key in filters.keys():
			value = filters[key]
			if key in keyMapping:
				truekey = keyMapping[key]
				translatedFilter[truekey] = value
		if "neuter__isnull" in translatedFilter:
			translatedFilter["neuter__isnull"] = not translatedFilter["neuter__isnull"]
		if "isMale" in translatedFilter:
			translatedFilter["isMale"] = True if translatedFilter["isMale"] =="male" else False
		#print(translatedFilter)
		return translatedFilter

	@staticmethod 
	def create( resourceDict, id=None):
		cat = Cat()
		if id:
			cat.id = id 
		cat.name = "N/A"
		cat.save()
		cat.patch(resourceDict)
		return cat 

	def patch(self, resourceDict):
		#print(resourceDict)
		if "ems" in resourceDict:
			self.ems = resourceDict['ems']

		self.name = resourceDict['name'] if "name" in resourceDict else self.name 
		self.country = resourceDict['country'] if "country" in resourceDict else self.country 
		self.registration_class = resourceDict['registration_class'] if "registration_class" in resourceDict else self.country 
		if "organization" in resourceDict:
			self.orginization_id = resourceDict["organization"]
		self.birth_date = resourceDict['birthdate'] if "birthdate" in resourceDict else self.birth_date
		if "gender" in resourceDict:
			self.isMale = resourceDict['gender'] == "male"
		self.sire_id = resourceDict['sire'] if "sire" in resourceDict else self.sire_id
		self.dam_id = resourceDict['dam'] if "dam" in resourceDict else self.dam_id
		self.cattery_id = resourceDict['cattery'] if "cattery" in resourceDict else self.cattery_id
		if "microchip" in resourceDict:
			mic = self.microchip()
			if mic:
				mic.microchip = resourceDict["microchip"]
				mic.save()
			else:
				mic = Microchip()
				mic.cat = self
				mic.microchip = resourceDict["microchip"]
		if "neutered" in resourceDict:
			neuter = resourceDict['neutered']
			if neuter and 'neutered_date' in resourceDict:
				if hasattr(self,"neuter"):
					self.neuter.date = resourceDict['neutered_date']
					self.neuter.save()
				else:
					n = Neuter()
					n.cat = self 
					n.date = resourceDict['neutered_date']
					n.save()
			elif neuter == False:
				if hasattr(self,"neuter"):
					self.neuter.delete()
		self.save()

class Import(models.Model):
	cat = models.OneToOneField('Cat',on_delete=models.CASCADE)
	organization = models.ForeignKey('organization',on_delete=models.CASCADE)
	country = models.CharField(max_length = 3)
	original_reg_date = models.DateField()
	original_reg_id = models.CharField(max_length = 20)
class Neuter(models.Model):
	cat = models.OneToOneField('Cat', primary_key = True,on_delete=models.CASCADE)
	date = models.DateField(null = True)
class Microchip(models.Model):
	id = models.AutoField(primary_key = True)
	cat = models.ForeignKey('Cat',on_delete=models.CASCADE)
	microchip = models.CharField(max_length = 30)
class Breed(models.Model):
	breed = models.CharField(max_length = 25, unique=True)
	category = models.IntegerField()
	short = models.CharField(max_length = 5,unique = True)
class Color(models.Model):
	color = models.CharField(max_length=50, unique = True)
	short = models.CharField(max_length=20, unique = True)
	desc = models.CharField(max_length=1024)
class EMS(models.Model):
	breed = models.ForeignKey('Breed',on_delete=models.CASCADE)
	color = models.ForeignKey('Color',on_delete=models.CASCADE)
	group = models.IntegerField(null = True)
	
	@staticmethod 
	def splitEms(emsString):
		b = emsString.split(" ")[0].upper().strip()
		c = " ".join(emsString.split(" ")[1:]).lower().strip()
		return (b,c)

	def toObject(self):
		ems = {}
		ems['ems'] = str(self)
		ems['breed'] = self.breed.breed
		ems['category'] = self.breed.category
		ems['breed_short'] = self.breed.short 
		ems['color'] = self.color.color
		ems['color_short'] = self.color.short
		ems['color_description'] = self.color.desc
		ems['group'] = self.group 
		return ems

	@staticmethod
	def apiMap(filters):
		keyMapping = {
			"ems":"ems",
			"breed":"breed__breed",
			"category":"breed__category",
			"breed_short":"breed__short",
			"color":"color__color",
			"color_short":"color__short",
			"color_description":"color__desc",
			"group":"group"
		}
		translatedFilter = {}
		for key in filters.keys():
			value = filters[key]
			if key in keyMapping:
				truekey = keyMapping[key]
				translatedFilter[truekey] = value
		if "ems" in translatedFilter:
			ems = translatedFilter['ems']
			translatedFilter.pop("ems",None)
			b = ems.split(" ")[0].upper().strip()
			c = " ".join(ems.split(" ")[1:]).lower().strip()
			if not "breed__short" in translatedFilter:
				translatedFilter["breed__short"] = b
			if not "color__short" in translatedFilter:
				translatedFilter["color__short"] = c
		return translatedFilter

	@staticmethod 
	def create(resourceDict, id=None):
		ems = EMS()
		rd = resourceDict
		if "ems" in rd:
			b,c = EMS.splitEms(rd["ems"])
			rd["breed_short"] = b if "breed_short" not in rd else rd["breed_short"]
			rd["color_short"] = c if "color_short" not in rd else rd["color_short"]
		if "breed_short" in rd:
			breed = Breed.objects.filter(short = rd["breed_short"])
			if len(breed) == 0:
				breed = Breed()
				if "breed" in rd:
					breed.breed = rd["breed"]
				else:
					breed.breed = rd["breed_short"]
				breed.short = rd["breed_short"]
				breed.category = rd["category"]
				breed.save()
			else:
				breed = breed[0]
			ems.breed = breed 
		if "color_short" in rd:
			color = Color.objects.filter(short = rd["color_short"])
			if len(color) == 0:
				color = Color()
				if "color" in rd:
					color.color = rd["color"]
				else:
					color.color = rd["color_short"]
				if "color_description" in rd:
					color.desc = rd["color_description"]
				color.short = rd["color_short"]
				color.save()
			else:
				color = color[0]
			ems.color = color 
		if "group" in rd:
			ems.group = rd["group"]
		else:
			ems.group = None
		ems.save()

		return ems 

	def patch(self, resourceDict):
		pass
		
	
	@staticmethod
	def getEMS(emsString):
		_a = emsString.split(" ")
		_b = _a[0].upper().strip()
		_c = " ".join(_a[1:]).lower().strip()
		b = Breed.objects.get(short = _b)
		c = Color.objects.get(short = _c)
		ems = EMS.objects.get(breed = b, color = c)
		return ems

	@property
	def ems(self):
	   return str(self)

	@property 
	def category(self):
	   return self.breed.category

	def __str__(self):
		return self.breed.short + " " + self.color.short
	
	class Meta:
		unique_together = ('breed', 'color')
class CatEms(models.Model):
	cat = models.ForeignKey('Cat',on_delete=models.CASCADE)
	ems = models.ForeignKey('EMS',on_delete=models.CASCADE)
	date = models.DateField()

	@property
	def category(self):
		return self.ems.category if self.ems else None
	@property 
	def breed(self):
		return self.ems.breed
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
	organizer = models.ForeignKey('Person',on_delete=models.CASCADE)
	date = models.DateField()
	location = models.CharField(max_length = 50, null=True)
	visibleToPublic = models.BooleanField(default = True)
	openForRegistration = models.BooleanField(default = False)
	international = models.BooleanField(default = True)

	def isOver(self):
		return date.today() < self.date
	@property
	def catsRegistered(self):
		return self.entry_set.all().count()
	def littersRegistered(self):
		return self.litter_set.all().count()
	def judges(self):
		allJudges = ShowJudges.objects.filter(show = self)
		return allJudges
	def judgements(self,lower = 0,count = 20):
		entries = Judgement.objects.filter(entry__show = self).order_by("entry__catalog_nr")[lower:lower+count]
		return entries
	def judgementsFilled(self):
		judgements = Judgement.objects.filter(entry__show = self, abs = False).count()
		return judgements
	def judgementsPending(self):
		judgements = Judgement.objects.filter(entry__show = self, abs__isnull = True).count()
		return judgements

	def awardCategories(self):
		cats = []
		for award in self.showaward_set.all():
			if award.award.category not in cats:
				cats.append(award.award.category)
		return cats

	
	@staticmethod
	def apiMap(filters):
		keyMapping = {
			"name":"name",
			"organizer":"organizer_id",
			"date":"date",
			"is_international":"international",
			"location":"location",
			"accepts_registrations":"openForRegistration",
			"is_visible_to_public":"visibleToPublic",
			"entrant_count":"catsRegistered",
			"judges":"showjudges_set__judge__id"
		}
		translatedFilter = {}
		for key in filters.keys():
			value = filters[key]
			if key in keyMapping:
				truekey = keyMapping[key]
				translatedFilter[truekey] = value
		return translatedFilter

	@staticmethod 
	def create(resourceDict, id = None):
		show = Show()
		if id:
			show.id = id 
		show.name = "N/A"
		show.organizer = None
		show.date = date.today()
		show.save()
		show.patch(resourceDict)
		return show 

	def patch(self, resourceDict):
		rd = resourceDict
		if "name" in rd:
			self.name = rd['name']
		if "organizer" in rd:
			self.organizer_id = rd['organizer']
		if "date" in rd:
			self.date = rd['date']
		if "is_international" in rd:
			self.international = rd['is_international']
		if "location" in rd:
			self.location = rd['location']
		if "accepts_registrations" in rd:
			self.openForregistration = rd['accepts_registrations']
		if "is_visible_to_public" in rd:
			self.visibleToPublic = rd['is_visible_to_public']
		if "awards_offered" in rd:
			aw = [x.award.id for x in self.showaward_set.all()]
			for award in rd['awards_offered']:
				if award not in aw:
					offer = showAward()
					offer.show = self
					offer.award_id = award 
					offer.save()
			for removed in aw:
				if removed not in rd['awards_offered']:
					award = ShowAward.objects.filter(show = self, award_id = removed)
					if len(award) == 1:
						award[0].delete()
		if "judges" in rd:
			ju = [x.judge.id for x in self.showjudges_set.all()]
			for judge in rd['judges']:
				if judge not in ju:
					sj = ShowJudges()
					sj.show = self
					sj.judge_id = judge
					sj.save()
			for removed in ju:
				if removed not in rd['judges']:
					judge = ShowJudges.objects.filter(show = self, judge_id = removed)
					if len(judge) == 1:
						judge[0].delete()
				
	def toObject(self):
		obj = {}
		obj["name"] = self.name 
		obj["organizer"] = self.organizer.id
		obj["date"] = self.date 
		obj["is_international"] = self.international
		obj["location"] = self.location 
		obj["accepts_registrations"] = self.openForRegistration
		obj["is_visible_to_public"] = self.visibleToPublic
		obj["entrant_count"] = self.catsRegistered 
		obj["judges"] = []
		for j in self.showjudges_set.all():
			obj['judges'].append(j.judge.id)
		obj["awards_offered"] = []
		for a in showAward.objects.filter(show = self):
			obj["awards_offered"].append(a.award.id)
		return obj
class Entry(models.Model):
	cat = models.ForeignKey('Cat',on_delete=models.CASCADE)
	show = models.ForeignKey('Show',on_delete=models.CASCADE)
	catalog_nr = models.IntegerField()
	guest = models.BooleanField() 	
	class Meta:
		unique_together = ('show', 'cat')
		unique_together = ('show', 'catalog_nr')

	
	@staticmethod
	def apiMap(filters):
		keyMapping = {
			"catalog_number":"catalog_nr",
			"show":"show_id",
			"is_guest":"guest",
			"cat":"cat_id",
			"judge":"judgement__judge__id",
			"judgement_ready":"judgement__abs__isnull",
			"is_biv":"judgement__biv",
			"was_absent":"judgement__abs",
			"judgement":"judgement__judgement",
			"judgement_comment":"judgement__comment",
			"recieved_certification":"judgement__catcert__isnull",
			"certification":"judgement__catcert__cert__fullname",
			"recieved_title":"judgement__catcert__cert__isnull",
			"title":"judgement__catcert__cert__title"
		}
		translatedFilter = {}
		for key in filters.keys():
			value = filters[key]
			if key in keyMapping:
				truekey = keyMapping[key]
				translatedFilter[truekey] = value
		if "judgement__catcert__isnull" in translatedFilter:
			translatedFilter["judgement__catcert__isnull"] = not translatedFilter["judgement__catcert__isnull"]
		if "judgement__catcert__cert__isnull" in translatedFilter:
			translatedFilter["judgement__catcert__cert__isnull"] = not translatedFilter["judgement__catcert__cert__isnull"]
		if "judgement__abs__isnull" in translatedFilter:
			translatedFilter["judgement__abs__isnull"] = not translatedFilter["judgement__abs__isnull"] 
		return translatedFilter

	@staticmethod 
	def create(resourceDict, id = None):
		entry = Entry()
		if id:
			entry.id = id 
		entry.patch(resourceDict)
		entry.save()
		return entry 

	def patch(self, resourceDict):
		rd = resourceDict
		#print(rd)
		j = Judgement.objects.filter(entry = self)
		if len(j) == 0:
			j = Judgement()
			j.entry = self 
			j.judge = None
			self.save()
			j.save()
		else:
			j = self.judgement 
		if "catalog_number" in rd:
			catnr = rd["catalog_number"]
			replacementTest = Entry.objects.filter(show = self.show, catalog_nr = catnr)
			if len(replacementTest) == 0:
				self.catalog_nr = catnr
			else:
				raise ValueError("Each entry at a show must have a unique catalog number. " + catnr +"is reserved for cat "+replacementTest[0].id)
		if "is_guest" in rd:
			self.guest = rd["is_guest"]
		if "cat" in rd:
			self.cat_id = rd["cat"]
		if "judge" in rd:
			j.judge_id = rd["judge"]
		if "is_biv" in rd:
			j.biv = rd["is_biv"]
		if "was_absent" in rd:
			j.abs = rd["was_absent"]
		if "judgement" in rd:
			j.judgement = rd["judgement"]
		if "judgement_comment" in rd:
			j.comment = rd["judgement_comment"]
		if "recieved_certification" in rd:
			j.certifications(rd["recieved_certification"])
		if "nominations" in rd:
			self.nominations(rd["nominations"])
		if "awards" in rd:
			j.awards(rd["awards"])
		j.save()
		self.save()

	def toObject(self):
		obj = {}
		obj["catalog_number"] = self.catalog_nr 
		obj["show"] = self.show.id
		obj["is_guest"] = self.guest 
		obj["cat"] = self.cat.id
		if self.judgement.judge:
			obj["judge"] = self.judgement.judge.id
		else:
			obj["judge"]=  None 
		if self.judgement.filled:
			obj["judgement_ready"] = True
			obj["is_biv"] = self.judgement.biv
			obj["was_absent"] = self.judgement.abs 
			obj["judgement"] = self.judgement.judgement
			obj["judgement_comment"] = self.judgement.comment
			if hasattr(self.judgement,"catcert"):
				obj["recieved_certification"] = True
				obj["certification"] = self.judgement.catcert.cert.fullName()
				if  self.judgement.catcert.cert.prev():
					obj["current_certification"] = self.judgement.catcert.cert.prev()
					t = self.judgement.catcert.cert.prev().getTitle()
					if t:
						obj["current_title"] = t.short
					else:
						obj["current_title"] = None

				else:
					obj["current_certification"] = None
					obj["current_title"] = None

				obj["next_certification"] = obj["certification"]
				if hasattr(self.judgement.catcert.cert,"title"):
					obj["recieved_title"] = True
					obj["title"] = self.judgement.catcert.cert.getTitle().short
				else:
					obj["recieved_title"] = False
			else:
				obj["recieved_certification"] = False
				currentCert = self.cat.highestCert(self.cat.isNeutered)
				if currentCert:
					obj["current_certification"] = currentCert.cert
					t = currentCert.cert.getTitle()
					if t:
						obj["current_title"]  = t.short
					else:
						obj["current_title"] = None
				else:
					obj["current_certification"] = None
					obj["current_title"] = None
				if currentCert:
					obj["next_certification"] = currentCert.cert.next.fullName()
				else:
					obj["next_certification"] = Cert.base(neutered = self.cat.isNeutered).fullName()
			obj["nominations"] = []
			obj["awards"] = []
			nomSet = Nomination.objects.filter(entry = self)
			for nom in nomSet:
				obj["nominations"].append(nom.award.name)
				if nom.bis:
					obj["awards"].append(nom.award.name)
		else:
			obj["judgement_ready"] = False
			highCert = self.cat.highestCert(self.cat.isNeutered)
			if highCert:
				obj["current_certification"] =highCert.cert
				obj["next_certification"] = highCert.cert.next.fullName()
				t =  highCert.cert.getTitle()
				if t:
					obj["current_title"] = t.short
				else:
					obj["current_title"] = None
			else:
				obj["current_certification"] = None
				obj["next_certification"] = Cert.base(neutered = self.cat.isNeutered).fullName()
				obj["current_title"] = None
		
		k = self.show.date + relativedelta(months=-7)
		j = self.show.date + relativedelta(months=-10)
		isKitten = self.cat.birth_date >= k
		isJunior = self.cat.birth_date >= j
	
		if isKitten:
			obj["current_certification"] = None
			obj["next_certification"] = None 
			obj['class'] = 12
		elif isJunior:
			obj["current_certification"] = None
			obj["next_certification"] = None 
			obj['class'] = 11
		else:
			if obj["current_certification"]:
				obj["class"] = obj["current_certification"].certClass
				obj["current_certification"] = obj["current_certification"].fullName()
			else:
				obj["class"] = Cert.base(neutered = self.cat.isNeutered).certClass
		return obj
class ShowJudges(models.Model):
	show = models.ForeignKey(Show,on_delete=models.CASCADE)
	judge = models.ForeignKey(Judge,on_delete=models.CASCADE)
	class Meta:
		unique_together = ('show','judge')

	def fullName(self):
		return self.judge.fullName()
class Judgement(models.Model):
	entry = models.OneToOneField('Entry', primary_key = True,on_delete=models.CASCADE)
	judge = models.ForeignKey('Judge', null=True, on_delete=models.CASCADE)
	judgement = models.CharField(max_length = 10, default = "") #EX1
	biv = models.BooleanField(default = False)
	abs = models.NullBooleanField(null = True)
	comment = models.CharField(max_length = 2048, default = "")

	@property
	def filled(self):
		return not abs is None 
	def date(self):
		return self.entry.show.date
	def cert(self):
		if hasattr(self,'catcert'):
			return self.catcert.cert
		else:
			return None
	def _catcert(self):
		if hasattr(self,'catcert'):
			return self.catcert
		else:
			return None
	@property 
	def nom(self):
		noms = Nomination.objects.filter(entry = self.entry)
		return [x for x in noms]
	
	#certifications(recieved). Sets or removes the certification relevant to this judgement. 
	def certifications(self, recieved):
		if recieved: #Award certification if not already awarded
			if self._catcert():
				pass
			else:
				c = CatCert()
				c.cat = self.entry.cat
				c.judgement = self
				cert = self.entry.cat.highestCert(self.entry.cat.isNeutered)
				if cert:
					c.cert = cert.cert.next
				else:
					c.cert = Cert.base(self.entry.cat.isNeutered)
				c.ems = self.entry.cat.ems.ems #Todo, use the EMS code that the cat *had* at the date of the show, not the most recent. 
				c.save()
		else: 
			#If the certification has already been given out, delete.
			#Future functionality: what to do if editing a show that's already passed? If the cat has other certifications above?
			if  self._catcert():
				self._catcert().delete()
class Litter(models.Model):
	class Meta:
		unique_together = ('show', 'catalog')
	catalog = models.CharField(max_length = 3)
	show = models.ForeignKey('Show',on_delete=models.CASCADE)
class LitterCat(models.Model):
	litter = models.ForeignKey('Litter',on_delete=models.CASCADE)
	entry = models.OneToOneField('Entry', primary_key = True,on_delete=models.CASCADE)
class LitterJudgement(models.Model):
	show = models.ForeignKey('Show',on_delete=models.CASCADE)
	judge = models.ForeignKey('Judge',on_delete=models.CASCADE)
	abs = models.BooleanField()
	rank = models.IntegerField()
	comment = models.CharField(max_length = 2048)
	litter = models.ForeignKey('Litter',on_delete=models.CASCADE)
class Cert(models.Model):
	name = models.CharField(max_length = 10)
	rank = models.IntegerField()
	next = models.ForeignKey('Cert', null=True,on_delete=models.CASCADE)
	certClass = models.IntegerField()
	neuter = models.BooleanField()

	def prev(self):
		certQ = Cert.objects.filter(next = self).exclude(id = self.id)
		if len(certQ) == 0:
			return None
		else:
			return certQ[0]
		
	def fullName(self):
		if self.next == self:
			return self.name
		else:
			return self.name + "-" + str(self.rank)

	def getTitle(self):
		if hasattr(self,'title'):
			return self.title
		else:
			if self.prev():
				return self.prev().getTitle()
			else:
				return None

	def absRank(self):
		c = getCache("Cert",self.id,"")
		if(c):
			#print(c)
			return c
		if(self.next):
			if self.next == self:
				setCache("Cert",self.id,"",1);
				return 1
			else:
				r = 1 + self.next.absRank()
				setCache("Cert",self.id,"", r);
				return r
		else:
			setCache("Cert",self.id,"",1);
			return 1

	def toObject(self):
		c = {}
		c['certification_group'] = self.name 
		c['rank'] = self.rank
		p = self.prev()
		if p:
			c['previous_certification'] = p.fullName()
		else:
			c['previous_certification'] = None

		
		n = self.next
		if n:
			c['next_certification'] = n.fullName()
			c['ultimate'] = n.name != self.name 
		else:
			c['next_certification'] = None
			c['ultimate'] = False
		c['certification'] = self.fullName()
		t = self.getTitle()
		c['title'] = t.name if t else None
		c['title_group'] = t.short if t else None
		c['is-neutered'] = self.neuter
		return c
		

	def apiMap(filters):
		pass


	@staticmethod
	def create(rd, id=None):
		pass

	def patch(self, rd):
		pass 
	@staticmethod
	def base(neutered = False):
		if neutered:
			return Cert.objects.get(name = "CAP", rank = 1)
		else:
			return Cert.objects.get(name = "CAC", rank = 1)
class CatCert(models.Model):
	cat = models.ForeignKey('Cat',on_delete=models.CASCADE)
	judgement = models.OneToOneField('Judgement', null=True,on_delete=models.CASCADE)
	cert = models.ForeignKey('Cert',on_delete=models.CASCADE)
	ems = models.CharField(max_length = 20, null=True)

	def title(self):
		return self.cert.getTitle()

	def absRank(self):
		return self.cert.absRank()
class Title(models.Model):
	name = models.CharField(max_length = 50)
	short = models.CharField(max_length = 10)
	cert = models.OneToOneField('Cert',null=True,on_delete=models.CASCADE)
class Nomination(models.Model):
	judge = models.ForeignKey('Judge', null=True, on_delete=models.CASCADE)
	entry = models.ForeignKey('Entry', on_delete = models.CASCADE)
	award = models.ForeignKey('Award',on_delete=models.CASCADE)
	bis = models.BooleanField(default = False)
	class Meta:
		unique_together = (('entry', 'award'))


	@property 
	def uri(self):
		#Todo, implement proper URI methods.
		a = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890";
		b = [17,7,37,97,2,47]
		l = len(a)
		uri = ""
		for i in range(10,16):
			_b = b[i%len(b)]
			uri += a[(_b + (i*_b)*(self.id + i + _b)) % l]
		return uri
	def toObject(self):
		o = {}
		o['judge'] = self.judge_id 
		o['entry'] = self.entry.catalog_nr
		o['show'] = self.entry.show_id
		o['cat'] = self.entry.cat_id
		o['award'] = self.award_id 
		o['award_name'] = self.award.name 
		o['award_category'] = self.award.category 
		o['bis'] = self.bis
		o['id'] = self.uri
		return o
	@staticmethod
	def create(rd,id = None):
		nom = Nomination()
		if id:
			nom.id = id
		entry = Entry.objects.get(catalog_nr = rd["entry"], show = rd["show"])
		nom.entry = entry
		nom.award_id = rd["award"]
		nom.save()
		nom.patch(rd)
		return nom 
	@staticmethod
	def apiMap(filters):
		keyMapping = {
			"judge":"judge_id",
			"entry":"entry__catalog_nr",
			"show":"entry__show_id",
			"award":"award_id",
			"award_name":"award__name",
			"award_category":"award__category",
			"bis":"bis"
		}
		translatedFilter = {}
		for key in filters.keys():
			value = filters[key]
			if key in keyMapping:
				truekey = keyMapping[key]
				translatedFilter[truekey] = value

		return translatedFilter
	def patch(self,rd):
		if "judge" in rd:
			self.judge_id = rd["judge"]
		if "entry" in rd:
			e = Entry.objects.get(show = self.entry.show, catalog_nr = rd["entry"])
			self.entry = e
		if "award" in rd:
			self.award_id = rd["award"]
		if "award_name" in rd:
			aw = Award.objects.filter(name = rd["name"])
			if len(aw) == 1:
				self.award = award 
		if "bis" in rd:
			self.bis = rd["bis"]
		self.save()
class LitterNomination(models.Model):
	judgement = models.ForeignKey('LitterJudgement',on_delete=models.CASCADE)
	award = models.ForeignKey('Award',on_delete=models.CASCADE)
class Award(models.Model):
	name = models.CharField(max_length = 50)
	coreAward = models.BooleanField(default = False)
	category = models.CharField(max_length = 50, null = True)
	ranking = models.IntegerField(default = 0)
	
	@staticmethod 
	def create(rd, id = None):
		award = Award()
		award.name = rd["name"]
		if "is_core" in rd:
			award.coreAward = rd["is_core"]
		else:
			award.coreAward = False
		if "category" in rd:
			award.category = rd["category"]
		award.save()
		return award

	@staticmethod
	def apiMap(filters):
		keyMapping = {
			"name":"name",
			"is_core":"coreAward",
			"category":"category"
		}
		translatedFilter = {}
		for key in filters.keys():
			value = filters[key]
			if key in keyMapping:
				truekey = keyMapping[key]
				translatedFilter[truekey] = value

		return translatedFilter

	def toObject(self):
		o = {}
		o['id'] = self.id 
		o['name'] = self.name
		o['is_core'] = self.coreAward 
		o['category'] = self.category 
		return o 
	def patch(self,rd):
		if "name" in rd:
			self.name = rd['name']
			
		if "is_core" in rd:
			self.coreAward = rd['is_core']

		if "category" in rd:
			self.category = rd['category']
		self.save()
class showAward(models.Model):
	show = models.ForeignKey('Show', on_delete = models.CASCADE)
	award = models.ForeignKey('Award', on_delete = models.CASCADE)
  #Auth
class Permissions(models.Model):
       id = models.BigIntegerField(primary_key = True)
       name = models.CharField(max_length=20, unique = True)
class MemberPermissions(models.Model):
       user = models.ForeignKey(Member,on_delete=models.CASCADE)
       permission = models.ForeignKey(Permissions,on_delete=models.CASCADE)
       class Meta:
               unique_together = (('user', 'permission'))
class Login_log(models.Model):
       id = models.AutoField(primary_key = True)
       user = models.ForeignKey(Member,on_delete=models.CASCADE)
       time = models.DateTimeField()
       lastRefresh = models.DateTimeField(null = True)
       expires = models.BooleanField(default = True)
       ip = models.CharField(max_length = 50)
       cookie = models.CharField(max_length = 256, unique = True, null = True)
