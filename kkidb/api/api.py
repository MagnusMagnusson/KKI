# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import QueryDict
from kkidb.auth import auth
from django.core.exceptions import ObjectDoesNotExist
from kkidb.models import *
from django.contrib.postgres.search import TrigramDistance
from django.db.models import Max
from django.db import transaction
from datetime import date
import json

DEBUG = True

def _get(model, id, queryObject = None):
	if queryObject == None:
		queryObject = model.objects.all()
	if id:
		_o = queryObject.get(id = id)
	else:
		_o = queryObject
	return JsonResponse({"success":True,"results":_o.toObject()})

def _gets(model,data, queryObject = None):
	page = 0
	offset = 25
	if queryObject == None:
		queryObject = model.objects.all()
	if "page" in data:
		page = data['page']
	if "offset" in data:
		offset = data['offset']
	_objects = queryObject
	if "filter" in data:
		filters = data['filter']
		filters = model.apiMap(filters)
		_objects = _objects.filter(**filters)
	if "search" in data:
		terms = data['search']
		terms = model.apiMap(terms)
		for term in terms.keys():
			_objects = _objects.annotate( distance=TrigramDistance(term, terms[term]),).filter(distance__lte=0.9).order_by("distance")
	lower = offset * page
	upper = offset * (page + 1)
	d = {'success':True, 'results':[]}
	for res in _objects[lower:upper]:
		results = res.toObject()
		d['results'].append(results)
	d['results'] = list(d['results'])
	return JsonResponse(d)

def _post(model, data, id = None):
		if(id):
			_otest = model.objects.filter(id = id)
			if len(_otest) > 0:
				return invalid("Resource already exists with id " +str(id)+" (Did you mean to use PUT or PATCH?)",True,409)
		_o = model.create(data,id)
		return valid(_o.toObject(),201)

def _put(model, data, id):
	try:
		_o = model.objects.get(id = id)
		return patch(model,data,id)
	except ObjectDoesNotExist:
		return post(model,data,id)

def _patch(model,data,id):
	try:
		_o = model.objects.get(id = id)
		_o.patch(data)
		return valid(_o.toObject(),200)
	except ObjectDoesNotExist as ex:
		if not DEBUG:
			return invalid("No resource located here with id "+str(id),True,404)
		else:
			raise ex

def defaultProcessGroup(model,request, queryObject = None):
	if request.method == "GET":
		if 'data' in request.GET:
			data = json.loads(request.GET['data'])
		else:
			data = {}
		return _gets(model,data,queryObject)
	elif request.method == "POST":
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		return _post(model,data)
	elif request.method == "PUT":
		return invalid("Invalid method " + request.method +", use POST instead", True, 405)
	elif request.method == "PATCH":
		return invalid("Multi-resource PATCH not implemented " + request.method, True, 501)
	elif request.method == "DELETE":
		return invalid("Invalid method " + request.method, True, 405)
	else:
		return invalid("Unknown method " + request.method, True, 400)

def defaultProcessSingular(model,request,id, queryObject = None):
	if request.method == "GET":
		return _get(model,id,queryObject)
	elif request.method == "POST":
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		catTest = model.objects.filter(id = id)
		if len(catTest) > 0:
			return invalid("Resource already exists. use PUT or PATCH",False,409)
		else:
			return post(Cat,data,id)
	elif request.method == "PUT":
		data = getData(request.body)
		return _put(model,data,id)
	elif request.method == "PATCH":
		data = getData(request.body)
		return _patch(model,data,id)
	elif request.method == "DELETE":
		return invalid("Illegal Method " + request.method, True, 403)
	else:
		return invalid("Unknown method " + request.method, True, 400)

#Cat
# operates on a single cat entity

def cat(request,id):
	return defaultProcessSingular(Cat,request,id)

#Cats
#Operates on the set of all gets
def cats(request):
	return defaultProcessGroup(Cat,request)

def member(request, id):
	if request.method == "GET":
		member = Member.objects.get(id = id)
		person = member.person
		return valid(person.toObject())
	elif request.method == "POST":
		#Attempts to create a member with the given ID. If the resource in question already exists 409(conflict) is returned. Returns 201(created) if successful.
		#If The
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		member = Member.objects.filter(id = id)
		if len(member) == 0:
			p = Person.create(-1,data)
			m = Member(id = id)
			m.person = p
			m.salt = "NOT SET"
			m.password = "NOT SET"
			m.save()
			return valid(p.toObject(),201)
		else:
			return invalid("Resource already exists",True,409)
	elif request.method == "PUT":
		data = getData(request.body)
		memberTest = Member.objects.filter(id = id)
		if len(memberTest) > 0:
			memberTest[0].patch(data)
			return JsonResponse(valid(c.toObject(),200))
		else:
			p = Person.create(-1, data)
			m = Member(id = id)
			m.person = p
			m.salt = "NOT SET"
			m.password = "NOT SET"
			m.save()
			return valid(p.toObject(),201)
	elif request.method == "PATCH":
		data = getData(request.body)
		member = Member.objects.filter(id = id)
		if len(member) == 0:
			return invalid("No member with the identification "+id,True,404)
		else:
			member[0].patch(data)
			return valid(member[0].toObject(),200)
	elif request.method == "DELETE":
		return invalid("Invalid method " + request.method, True, 405)
	else:
		return invalid("Unknown method " + request.method, True, 400) 

def members(request):
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
		members = Person.objects.filter(member__isnull = False)
		if "filter" in data:
			filters = data['filter']
			filters = Person.apiMap(filters)
			members = members.filter(**filters)
		if "search" in data:
			terms = data['search']
			terms = Person.apiMap(terms)
			for term in terms.keys():
				members = members.annotate( distance=TrigramDistance(term, terms[term]),).filter(distance__lte=0.9).order_by("distance")
		lower = offset * page
		upper = offset * (page + 1)
		d = {'success':True, 'results':[]}

		for res in members[lower:upper]:
			results = res.toObject()
			d['results'].append(results)
		d['results'] = list(d['results'])
		return JsonResponse(d)
	elif request.method == "POST":
		#Attempts to create a member. returns 201 if successful  
		#Returns the new object
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		p = Person()
		p.name = "N/A"
		p.save()
		p.patch(data)
		if not hasattr(p, "member"):
			m = Member()
			m.person = p
			m.save()
		return valid(p.toObject(),201)
	elif request.method == "PUT":
		return invalid("Invalid method " + request.method +", use POST instead", True, 405)
	elif request.method == "PATCH":
		return invalid("Multi-resource PATCH not implemented " + request.method, True, 501)
	elif request.method == "DELETE":
		return invalid("Invalid method " + request.method, True, 405)
	else:
		return invalid("Unknown method " + request.method, True, 400)

@transaction.atomic
def payments(request,id):
	if request.method == "GET":
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
		member = Member.objects.get(id = id)
		payments = MemberPayment.objects.filter(member = member)
		if "filter" in data:
			filters = data['filter']
			filters = MemberPayment.apiMap(filters)
			payments = payments.filter(**filters)
		if "search" in data:
			terms = data['search']
			terms = MemberPayment.apiMap(terms)
			for term in terms.keys():
				payments = payments.annotate( distance=TrigramDistance(term, terms[term]),).filter(distance__lte=0.9).order_by("distance")
		lower = offset * page
		upper = offset * (page + 1)
		d = {'success':True, 'results':[]}

		for res in payments[lower:upper]:
			results = res.payment.toObject()
			d['results'].append(results)
		d['results'] = list(d['results'])
		return JsonResponse(d)
	elif request.method == "POST":
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		payment = Payment()
		payment.patch(data)
		payment.save()
	elif request.method == "PUT":
		return invalid("Invalid method " + request.method+", use POST instead", True, 405)
	elif request.method == "PATCH":
		return invalid("Invalid method " + request.method, True, 405)
	elif request.method == "DELETE":
		return invalid("Invalid method " + request.method, True, 405)
	else:
		return invalid("Unknown method " + request.method, True, 400)

def payment(request,mid,gid):
	if request.method == "GET":
		#verify that the payment in question matches the member
		try:
			payment = Payment.objects.get(uri = gid)
			member = Member.objects.get(id = mid)
		except Exception as ex:
			return invalid("No payment with id " + gid + " and member " + str(mid)+ " found", 404)
		memberPayment = MemberPayment.objects.filter(member = member, payment = payment)
		if len(memberPayment) == 0:
			return invalid("No payment with specified ID "+gid+" belonging to member " +mid,404)
		else:
			return valid(payment.toObject())

	elif request.method == "POST":
		#pass
		pass
	elif request.method == "PUT":
		return invalid("Invalid method " + request.method, True, 405)
	elif request.method == "PATCH":
		return invalid("Invalid method " + request.method, True, 405)
	elif request.method == "DELETE":
		return invalid("Invalid method " + request.method, True, 405)
	else:
		return invalid("Unknown method " + request.method, True, 400)
	
def cattery(request, id):
	return defaultProcessSingular(Cattery,request,id)

def catteries(request):
	return defaultProcessGroup(Cattery,request)

def shows(request):
	return defaultProcessGroup(Show,request)

def show(request,id):
	return defaultProcessSingular(Show,request,id,)

@transaction.atomic
def entrants(request,sid):
	if request.method == "GET":
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
		entrants = Entry.objects.filter(show_id = sid)
		if "filter" in data:
			filters = data['filter']
			filters = Entry.apiMap(filters)
			entrants = entrants.filter(**filters)
		if "search" in data:
			terms = data['search']
			terms = Entry.apiMap(terms)
			for term in terms.keys():
				entrants = entrants.annotate( distance=TrigramDistance(term, terms[term]),).filter(distance__lte=0.9).order_by("distance")
		lower = offset * page
		upper = offset * (page + 1)
		d = {'success':True, 'results':[]}

		for res in entrants[lower:upper]:
			results = res.toObject()
			d['results'].append(results)
		d['results'] = list(d['results'])
		return JsonResponse(d)
	elif request.method == "POST":
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		entrant = Entry()
		entrant.show_id = sid
		entrant.patch(data)
	elif request.method == "PUT":
		return invalid("Invalid method " + request.method+", use POST instead", True, 405)
	elif request.method == "PATCH":
		return invalid("Invalid method " + request.method, True, 405)
	elif request.method == "DELETE":
		return invalid("Invalid method " + request.method, True, 405)
	else:
		return invalid("Unknown method " + request.method, True, 400)

@transaction.atomic
def entrant(request,sid,eid):
	if request.method == "GET":
		#verify that the payment in question matches the member
		try:
			e = Entry.objects.get(show_id = sid, catalog_nr = eid)
			return valid(e.toObject(),200)
		except ObjectDoesNotExist:
			return invalid("No entrant "+str(eid)+ " in show "+str(sid),404)

	elif request.method == "POST":
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		data['show'] = sid 
		e = Entry.create(data,eid)
		return valid(e.toObject(),201)
	elif request.method == "PUT":
		return invalid("Invalid method " + request.method, True, 405)
	elif request.method == "PATCH":
		try:
			data = getData(request.body)
			_o = Entry.objects.get(show_id = sid, catalog_nr = eid)
			_o.patch(data)
			return valid(_o.toObject(),200)
		except ObjectDoesNotExist as ex:
			if not DEBUG:
				return invalid("No resource located here with id "+str(eid),True,404)
			else:
				raise ex
	elif request.method == "DELETE":
		return invalid("Invalid method " + request.method, True, 405)
	else:
		return invalid("Unknown method " + request.method, True, 400)

def ems(request):
	return defaultProcessGroup(EMS,request)

def breed(request,breed):
	_b = Breed.objects.get(short = breed.upper().strip())
	_e = EMS.objects.filter(breed = _b)
	return defaultProcessGroup(EMS,request,_e)

def color(request,breed,color):
	col = " ".join(color.split("_"))
	ems = EMS.getEMS(breed + " " + col)
	return defaultProcessSingular(EMS,request,None,ems)

def cert(request,name,rank):
	if request.method == "GET":
		try:
			print(name,rank)
			c = Cert.objects.get(name = name, rank = rank)
			return valid(c.toObject(),200)
		except ObjectDoesNotExist as ex:
			if not DEBUG:
				return invalid("No resource at this location",True,404)
			else:
				raise ex
	else: 
		return invalid("Invalid method " + request.method, True, 405)

def hpCert(request):
	c = Cert.objects.filter(name = "HP")
	a = [e.toObject() for e in c]
	return valid(a,200)
def certs(request):
	return defaultProcessGroup(Cert,request)

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

def getData(body):
	_d = QueryDict(body)
	if 'data' in _d:
		data = json.loads(_d['data'])
	else:
		data = {}
	return data