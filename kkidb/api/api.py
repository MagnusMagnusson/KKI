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


#NewApi

#Cat
# operates on a single cat entity
def cat(request,id):
	if request.method == "GET":
		cat = Cat.objects.get(id = id)
		#Returns the cat with the designated id. 
		#Accepts no data.
		return JsonResponse({"success":True,"results":cat.toObject()})
	elif request.method == "POST":
		#Attempts to create a cat with the given ID. If the resource in question already exists 409(conflict) is returned. Returns 201(created) if successful 
		#Arguments: <str:birthdate> <int:cattery> <str:class> <str:country> <str:organization> <str:registry_digits> 
		#<int:dam> <int:sire> <str:ems> <str:gender> <str:microchip_number> <str:name> 
		#required: birthdate, class, organization, registry_digits, country, gender, microchip, name.
		#Returns the created object
		
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		catTest = Cat.objects.filter(id = id)
		if len(catTest) > 0:
			return invalid("Resource already exists. use PUT or PATCH",False,409)
		else:
			c = Cat.create(id, data)
			return JsonResponse(valid(c.toObject,201))
	elif request.method == "PUT":
		#Attempts to create a cat with the given ID. If the resource in question already exists it will be patched. returns 201 for created, 200 if patched 
		#Arguments: <str:birthdate> <int:cattery> <str:class> <str:country> <str:organization> <str:registry_digits> 
		#<int:dam> <int:sire> <str:ems> <str:gender> <str:microchip_number> <str:name> 
		#required: birthdate, class, organization, registry_digits, country, gender, microchip, name.
		#Returns the affected object
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		catTest = Cat.objects.filter(id = id)
		if len(catTest) > 0:
			catTest[0].patch(data)
			return JsonResponse(valid(c.toObject(),200))
		else:
			c = Cat.create(id, resource)
			return JsonResponse(valid(c.toObject(),201))
	elif request.method == "DELETE":
		return invalid("Illegal Method " + request.method, True, 403)
	else:
		return invalid("Unknown method " + request.method, True, 400)

#Cats
#Operates on the set of all gets
def cats(request):
	if request.method == "GET":
		#Returns the set of all cats (by default 25, can be modified via offset) that matches the filters and search terms 
		#Valid keys: <int:page>, <int:offset>, <dict:filter>, <dict:search>
		#returns: success, results
		if 'data' in request.GET:
			data = json.loads(request.GET['data'])
		else:
			data = {}
		page = 0
		offset = 25
		if "page" in data:
			page = data['page']
		if "offset" in data:
			offset = data['offset']
		cats = Cat.objects.all()
		if "filter" in data:
			filters = data['filter']
			filters = Cat.apiMap(filters)
			cats = cats.filter(**filters)
		if "search" in data:
			terms = data['search']
			terms = Cat.apiMap(terms)
			for term in terms.keys():
				cats = cats.annotate( distance=TrigramDistance(term, terms[term]),).filter(distance__lte=0.9).order_by("distance")
		lower = offset * page
		upper = offset * (page + 1)
		d = {'success':True, 'results':[]}
		for res in cats[lower:upper]:
			results = res.toObject()
			d['results'].append(results)
		d['results'] = list(d['results'])
		return JsonResponse(d)
	elif request.method == "POST":
		#Attempts to create a cat. returns 201 if successful  
		#Arguments: <str:birthdate> <int:cattery> <str:class> <str:country> <str:organization> <str:registry_digits> 
		#<int:dam> <int:sire> <str:ems> <str:gender> <str:microchip_number> <str:name> 
		#required: birthdate, class, organization, registry_digits, country, gender, microchip, name.
		#Returns the new object
		if 'data' in request.GET:
			data = json.loads(request.GET['data'])
		else:
			data = {}
		c = Cat()
		c.name = "N/A"
		c.save()
		c.patch(data)
		return valid(c.toObject(),201)
	elif request.method == "PUT":
		return invalid("Invalid method " + request.method +", use POST instead", True, 405)
	elif request.method == "PATCH":
		return invalid("Multi-resource PATCH not implemented " + request.method, True, 501)
	elif request.method == "DELETE":
		return invalid("Invalid method " + request.method, True, 405)
	else:
		return invalid("Unknown method " + request.method, True, 400)




#	if request.method == "GET":
#		return invalid("Invalid method " + request.method, True, 405)
#	elif request.method == "POST":
#		return invalid("Invalid method " + request.method, True, 405)
#	elif request.method == "PUT":
#		return invalid("Invalid method " + request.method, True, 405)
#		return invalid("Invalid method " + request.method, True, 405)
#	elif request.method == "DELETE":
#		return invalid("Invalid method " + request.method, True, 405)
#	else:
#		return invalid("Unknown method " + request.method, True, 400)

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


def invalid(message, fatal = False, code = 200):
	d = {
		'success':False,
		'error': message,
		'fatal': fatal
	}
	return JsonResponse( d, status = code)

def valid(message, code = 200):
	d = {
		'success':True ,
		'results':message
	}
	return JsonResponse(d,status = code)