# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import JsonResponse
from kkidb.auth import auth
from kkidb.models import *
from django.contrib.postgres.search import TrigramDistance
from django.db.models import Max
from datetime import date
import json


def getObjectset(type):
	if type == 'member':
		objectset = Person.objects.filter(member__isnull = False)
	elif type == 'cattery':
		objectset = Cattery.objects
	elif type == 'cat':
		objectset = Cat.objects
	elif type == 'person':
		objectset = Person.objects
	elif type == 'judge':
		objectset = Person.objects.filter(judge__isnull = False)
	else:
		objectset = Cat.objects.none()

	return objectset

def applyFilters(querySet, filters, objectType):
	if objectType == 'cat':
		if 'gender' in filters:
			isMale = filters['gender'] == 'sire'
			querySet = querySet.filter(isMale = isMale)
		if 'neutered' in filters:
			neutered = not filters['neutered']
			querySet = querySet.filter(neuter__isnull = neutered)
	return querySet


def login(request):
	if not request.is_ajax():
		D = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	member = validate_login(request)	
	if(member):		
		D = {
			'success':False,
			'error': "Þú ert núþegar innskráður"
		}
		return JsonResponse(D)
	pWord = str(request.POST['password']);
	uName = str(request.POST['user']);
	meta = request.META['HTTP_USER_AGENT']
	access = auth.log_in(uName,pWord,meta);
	if not access[0]:
		D = {
			'success':False,
			'error': "Rangt notendanafn/lykilorð"
			
		}		
		return JsonResponse(D)
	else:
		request.session.cycle_key()
		request.session['logged_in'] = True
		request.session['token'] = access[1]
		pid = Person.objects.get(email=uName)
		request.session['user'] = pid.name
		request.session.set_expiry(0)
		D = {
			'success':True
		}
		return JsonResponse(D)

def find(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)
	if 'json' in request.GET:
		try:
			request.GET = json.loads(request.GET['json'])
		except ValueError as e:
			return JsonResponse({'success':False, 'error':'Malformed JSON recieved'})

	type = request.GET['type'].lower()
	term = request.GET['term']
	value = request.GET['value']
	
	objectset = getObjectset(type)
	d = {}
	d['results'] = []
	q = objectset.annotate( distance=TrigramDistance(term, value),).filter(distance__lte=0.9).order_by('distance')
	
	if 'filters' in request.GET:
		q = applyFilters(q,request.GET['filters'], type)
	
	for res in q[:25]:
		results = res.toObject()
		d['results'].append((res.distance, results))
	d['results'] = list(d['results'])
	return JsonResponse(d)
	
def get_person(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)
	Q = Person.objects.all()
	get = request.GET
	d = {}
	valid = False
	d['results'] = []
	d['success'] = True
	if('ssn' in get):
		valid = True 
		Q = Q.filter(ssn = request.GET['ssn'])
	if('member' in get):
		Q = Q.filter(member__isnull = False)
		valid = True
	if 'name' in get:
		Q = Q.filter(name = get['name'])
	for res in Q:
		member = res.toObject()
		d['results'].append( member)

	if(not valid):
		d = {"success":False,'error':"Tilgreindu í það minnsta einn leitarramma"}
	return JsonResponse(d)

def get_cat(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)
	Q = Cat.objects.all()
	get = request.GET
	d = {}
	valid = False
	d['results'] = []
	d['success'] = True
	if('registry' in get):
		valid = True 
		Q = Q.filter(reg_full__contains = request.GET['registry'])
	if('id' in get):
		Q = Q.filter(id = get['id'])
		valid = True
	
	for res in Q:
		member = res.toObject()
		d['results'].append( member)

	if(not valid):
		d = {"success":False,'error':"Tilgreindu í það minnsta einn leitarramma"}
	return JsonResponse(d)

def get(request):
	if False and not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	dat = json.loads(request.GET['data'])
	type = dat['type'].lower()
	values = dat['values']

	objectSet = getObjectset(type)
	object = objectSet.filter(**values)
	if len(object) == 0:
		d = {
			'success':True,
			'results':None
		}
	else:
		d = {
		'success':True,
		'results': object[0].toObject()
	}
	return JsonResponse(d)


def submit_payment(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	post = json.loads(request.POST['data'])
	if('id' in post):
		payment = Payment.objects.get(id = post['id'])
	else:
		payment = Payment()
	payment.date = post['date']
	payment.payer = Person.objects.get(id = post['pid']).member
	payment.method = post['method']
	payment.giftYear = post['method'] == "free"
	payment.save()

	memberList = {payment.payer.person}

	for people in post['dependancies']:
		per = Person.objects.get(id = people)
		memberList.add(per)
	payment.updateMembers(memberList)

	response = {'success':True}
	return JsonResponse(response)

def submit_person(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	post = json.loads(request.POST['data'])
	if('id' in post):
		person = Person.objects.get(id = post['id'])
	else:
		person = Person()
	if "name" in post:
		person.name = post['name']
	if "address" in post:
		person.address = post['address']
	if "post" in post:
		person.postcode = post['post']
	if "city" in post:
		person.city = post['city']
	if "phone" in post:
		person.phone = post['phone']
	if "country" in post:
		person.country = post['country']
	if "email" in post:
		person.email = post['email']
	if "ssn" in post:
		person.ssn = post['ssn']

	person.save()

	response = {'success':True, 'result':person.toObject()}
	return JsonResponse(response)

def submit_member(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	post = json.loads(request.POST['data'])
	if('mid' in post):
		member = Member.objects.get(id = post['mid'])
	else:
		member = Member()

	if "pid" in post:
		person = Person.objects.get(id = post['pid'])		
		if(hasattr(person, 'member')):
			response = {'success':False, 'error':"Person already a member"}
			return JsonResponse(response)
		member.person = person
	else:
		response = {'success':False, 'error':"Must specify a person to become member"}
		return JsonResponse(response)


	member.save()

	response = {'success':True, 'result':member.toObject()}
	return JsonResponse(response)

def submit_cattery(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	post = json.loads(request.POST['data'])
	if('id' in post):
		cattery = Cattery.objects.get(id = post['id'])
	else:
		cattery = Cattery()
	if 'name' in post:
		cattery.name = post['name']
	if 'date' in post:
		cattery.registry_date = post['date']
	if 'country' in post:
		cattery.country = post['country']
	if 'orginization' in post:
		cattery.organization = Organization.objects.get(id = post['organization'])
	if 'prefix' in post:
		cattery.prefix = post['prefix'] == "prefix"
	if 'address' in post:
		cattery.address = post['address']
	if 'city' in post:
		cattery.city = post['city']
	if 'postcode' in post:
		cattery.postcode = post['post']
	if 'phone' in post:
		cattery.phone = post['phone']
	if 'email' in post:
		cattery.email = post['email']
	if 'website' in post:
		cattery.website = post['website']

	cattery.save() 
	if 'owners' in post:
		ownerList = []
		for people in post['owners']:
			per = Person.objects.get(id = people)
			ownerList.append(per)	
		cattery.updateMembers(ownerList)

	response = {'success':True}
	return JsonResponse(response)

def submit_neuter(request):

	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	post = json.loads(request.POST['data'])
	if('id' in post):
		cat = Cat.objects.get(id = post['id'])
	else:
		return JsonResponse({'success':False, 'error':"Enginn köttur tilgreindur"})
	if 'date' in post and post['date'] != "":
		date = post['date']
	else:
		return JsonResponse({'success':False, 'error':"Engin dagsetning tilgreind"})

	neuterTest = Neuter.objects.filter(cat = cat)
	if len(neuterTest ) == 0:
		neuter = Neuter()
		neuter.cat = cat
		neuter.date = date
		neuter.save()

	response = {'success':True}
	return JsonResponse(response)

def submit_cat(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	post = json.loads(request.POST['data'])
	new = 'id' not in post
	if('id' in post and post['id'] != ""):
		cat = Cat.objects.get(id = post['id'])
	else:
		cat = Cat()

	today = date.today()
	cat.reg_date = today
	if "birth" in post:
		cat.birth_date = post['birth']
	elif new:
		return invalid("field 'birth' not specified in request")
	if 'cattery' in post:
		cat.cattery = Cattery.objects.get(id = post['cattery'])
	elif new:
		return invalid("field 'cattery' not specified in request")

	if 'class' in post and 'country' in post and 'org' in post and 'reg_nr' in post:
		full_reg = post['country'] + " " + post['org'] + " " + post['class'] + " " + post['reg_nr']
		if post['country'].strip() == "" or post['org'].strip() == "" or post['class'] == "" or post['reg_nr'] == "":
			return invalid ("Malformed registration number")
		cat.reg_full = full_reg 
		cat.reg_nr = post['reg_nr']
	elif new:
		return invalid("Malformed registration number")

	if 'dam' in post:
		cat.dam = Cat.objects.get(id = post['dam'])
	elif new:
		return invalid("No dam specified")

	if 'sire' in post:
		cat.sire = Cat.objects.get(id = post['sire'])
	elif new:
		return invalid("no sire specified")

	if 'ems' in post:
		breedString = post['ems'][:3].upper().strip()
		colorString = post['ems'][3:].lower().strip()
		breed = Breed.objects.filter(short = breedString)
		if len(breed) > 0:
			breed = breed[0]
		else:
			return invalid("Unknown breed " + breedString)
		
		color = Color.objects.filter(short = colorString)
		if len(color) > 0:
			color = color[0]
		else:
			color = Color()
			color.short = colorString
			color.save()
		ems = EMS.objects.filter(breed = breed, color = color)
		if len(ems) == 1:
			ems = ems[0]
		elif len(ems) == 0:
			ems = EMS()
			ems.breed = breed
			ems.color = color 
			ems.save()
		else:
			return invalid("Contact administrator, multiple EMS match string")
		cems = CatEms()
		cems.ems = ems
		cems.date = today
	elif new:
		return invalid("No EMS specified")

	if 'gender' in post:
		if post['gender'] == 'male':
			cat.isMale = True
		elif post['gender'] == 'female':
			cat.isMale = False
		else:
			return invalid("gender must be 'male' or 'female'")
	elif new:
		return invalid('gender not specified')

	if 'microchip' in post:
		chipNumber = post['microchip'].strip()
		if len(chipNumber) <= 3:
			return invalid("Microchip number must be longer than three characters")
		micro = Microchip()
		micro.microchip = chipNumber
	elif new:
		return invalid("Microchip not specified")

	if 'name' in post:
		if len(post['name'].strip()) == 0:
			return invalid("Cat name cannot be empty")
		cat.name = post['name']
	elif new:
		return invalid('Name not specified')

	cat.save()
	cems.cat = cat 
	cems.save()
	micro.cat = cat
	micro.save()

	response = {'success':True, 'result':{'id':cat.id}}
	return JsonResponse(response)


def submit_ownership_change(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	post = json.loads(request.POST['data'])
	if('id' in post):
		cat = Cat.objects.get(id = post['id'])
	else:
		return JsonResponse({"success":False, "error":"Enginn köttur tilgreindur"})
	if 'date' in post:
		date = post['date']
	else:
		return JsonResponse({"success":False, "error":"Engin dagsetning tilgreind"})
	if 'owners' in post:
		ownerList = []
		resultOwnerList = []
		for people in post['owners']:
			per = Person.objects.get(id = people)
			ownerList.append(per)	
		cat.updateOwners(ownerList, date)
	else:
		return JsonResponse({'success':False,'error':"Engir eigendur tilgreinidir"})

	
	response = {'success':True, "results":{"owners":[x.toObject() for x in cat.owners()]}}
	return JsonResponse(response)

def submit_show(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	post = json.loads(request.POST['data'])

	show = Show()

	if 'mid' in post:
		show.organizer = Member.objects.get(id = post['mid']).person
	if 'showDate' in post:
		show.date = post['showDate']
	if 'showLocation' in post:
		show.location = post['showLocation']
	if 'showName' in post:
		show.name = post['showName']
	show.save()

	data = {
		'success': True,
		'result':{
			'id': show.id	
		}
	}

	return JsonResponse(data)

def next_regid(request):
	max =  1 + Cat.objects.all().exclude(reg_nr__gt = 9000).aggregate(Max('reg_nr'))['reg_nr__max']
	if max >= 9000:
		max =  1 + Cat.objects.all().aggregate(Max('reg_nr'))['reg_nr__max']
	return JsonResponse({'result':max})



def validate_login(request):
	if('token' in request.session):
		meta = request.META['HTTP_USER_AGENT']
		member = auth.validate_login(request.session['token'],meta)
		return member
	else:
		return None


def invalid(message, fatal = False):
	d = {
		'success':False,
		'error': message,
		'fatal': fatal
	}
	return JsonResponse(d)
