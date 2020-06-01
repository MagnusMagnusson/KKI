# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import QueryDict
from django.core.exceptions import ObjectDoesNotExist
from kkidb.models import *
from django.contrib.postgres.search import TrigramDistance
from django.db.models import Max
from django.db import transaction
import math
from datetime import date
from datetime import datetime
import json

DEBUG = False

def _get(model, id, queryObject = None):
	if queryObject == None:
		queryObject = model.objects.all()
	if id:
		_o = queryObject.get(id = id)
	else:
		_o = queryObject
	return JsonResponse({"success":True,"results":_o.toObject()})

def _gets(model,data, queryObject = None):
	try:
		print("aaa")
		page = 0
		offset = 25
		search_threshold = 0.9
		if queryObject == None:
			queryObject = model.objects.all()
		if "page" in data:
			page = data['page']
		if "offset" in data:
			offset = data['offset']
		if "search_threshold" in data:
			threshold = data['search_threshold']
		_objects = queryObject

		if "filter" in data:
			filters = data['filter']
			filters = model.apiMap(filters)
			_objects = _objects.filter(**filters)
	

		if "search" in data:
			terms = data['search']
			terms = model.apiMap(terms)
			for term in terms.keys():
				_objects = _objects.annotate( distance=TrigramDistance(term, terms[term]),).filter(distance__lte=search_threshold).order_by("distance")
	

		if offset > 0:
			lower = offset * page
			upper = offset * (page + 1)
			totalPage = math.ceil(len(_objects) / offset)
		else:
			lower = 0
			upper = len(_objects) + 1
			totalPage = 1
	
		d = {'success':True, 'results':[], 'count':len(_objects), "page":page, "total_pages":totalPage}
	
		_objects = _objects[lower:upper]
		d['results'] = [x.toObject() for x in _objects]
	
		d['results'] = list(d['results'])

		return JsonResponse(d)
	except ObjectDoesNotExist as ex:
		return invalid("Resource does not exist",404)

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
			return invalid("Resource does not exist",True,404)
		else:
			raise ex

def _delete(model,data,id):
	try:
		_o = model.objects.get(id = id)
		_o.delete()
		return valid({},200)
	except ObjectDoesNotExist as ex:
		if not DEBUG:
			return invalid("Resource does not exist",True,404)
		else:
			raise ex

def defaultProcessGroup(model,request, queryObject = None, extraData = {}):
	if request.method == "GET":
		if 'data' in request.GET:
			data = json.loads(request.GET['data'])
		else:
			data = {}
		if extraData:
			for key in extraData:
				data[key] = extraData[key]
		return _gets(model,data,queryObject)
	elif request.method == "POST":
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		if extraData:
			for key in extraData:
				data[key] = extraData[key]
		return _post(model,data)
	elif request.method == "PUT":
		return invalid("Invalid method " + request.method +", use POST instead", True, 405)
	elif request.method == "PATCH":
		return invalid("Multi-resource PATCH not implemented " + request.method, True, 501)
	elif request.method == "DELETE":
		return invalid("Invalid method " + request.method, True, 405)
	else:
		return invalid("Unknown method " + request.method, True, 400)

def defaultProcessSingular(model,request,id, queryObject = None, extraData = {}):
	if request.method == "GET":
		try:
			print("Hererererereeeeeeeeeee")
			return _get(model,id,queryObject)
		except ObjectDoesNotExist as ex:
			print("REEEEEEEEEEEEEE")
			if DEBUG:
				raise ex
			else:
				return invalid("Resource does not exist",False,404)
	elif request.method == "POST":
		if 'data' in request.POST:
			data = json.loads(request.POST['data'])
		else:
			data = {}
		if extraData:
			for key in extraData:
				data[key] = extraData[key]
		catTest = model.objects.filter(id = id)
		if len(catTest) > 0:
			return invalid("Resource already exists. use PUT or PATCH",False,409)
		else:
			return post(Cat,data,id)
	elif request.method == "PUT":
		data = getData(request.body)
		if extraData:
			for key in extraData:
				data[key] = extraData[key]
		return _put(model,data,id)
	elif request.method == "PATCH":
		data = getData(request.body)
		if extraData:
			for key in extraData:
				data[key] = extraData[key]
		return _patch(model,data,id)
	elif request.method == "DELETE":
		return _delete(model,{},id)
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
	return defaultProcessSingular(Show,request,id)

def award(request,id):
	return defaultProcessSingular(Award,request,id)

def awards(request):
	return defaultProcessGroup(Award,request)

def judge(request,id):
	return defaultProcessSingular(Judge,request,id)

def judges(request):
	return defaultProcessGroup(Judge,request)


def organization(request,id):
	return defaultProcessSingular(Organization,request,id)

def organizations(request):
	return defaultProcessGroup(Organization,request)

def people(request):
	return defaultProcessGroup(Person,request)

def person(request,id):
	return defaultProcessSingular(Person,request,id)

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

		if offset > 0:
			lower = offset * page
			upper = offset * (page + 1)
			totalPage = math.ceil(len(entrants) / offset)
		else:
			lower = 0
			upper = len(entrants) + 1
			totalPage = 1
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
				return invalid("Resource does not exist",True,404)
			else:
				raise ex
	elif request.method == "DELETE":
		return invalid("Invalid method " + request.method, True, 405)
	else:
		return invalid("Unknown method " + request.method, True, 400)

def ems(request):
	return defaultProcessGroup(EMS,request)

def breed(request,breed):
	try:
		_b = Breed.objects.get(short = breed.upper().strip())
		_e = EMS.objects.filter(breed = _b)
		return defaultProcessGroup(EMS,request,_e)
	except ObjectDoesNotExist as ex:
		return invalid("Resource does not exist",False,404)

def color(request,breed,color):
	try:
		col = " ".join(color.split("_"))
		ems = EMS.getEMS(breed + " " + col)
		return defaultProcessSingular(EMS,request,None,ems)
	except ObjectDoesNotExist as ex:
		if DEBUG:
			raise ex
		else:
			return invalid("Resource does not exist", False, 404)


def cert(request,name,rank):
	if request.method == "GET":
		try:
			print(name,rank)
			c = Cert.objects.get(name = name, rank = rank)
			return valid(c.toObject(),200)
		except ObjectDoesNotExist as ex:
			if not DEBUG:
				return invalid("Resource does not exist",True,404)
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

def nominations(request, sid):
	noms = Nomination.objects.filter(entry__show_id = sid)
	ed = {
		"show":sid
	}
	return defaultProcessGroup(Nomination,request,queryObject = noms, extraData = ed)

def nomination(request, sid, uri):
	noms = Nomination.objects.filter(entry__show_id = sid)
	noms = [x for x in noms if x.uri == uri]
	return defaultProcessSingular(Nomination,request,noms[0].id)

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
		return invalid("User already logged in", False, 200)
	pWord = str(request.POST['password']);
	uName = str(request.POST['user']);
	meta = request.META['HTTP_USER_AGENT']
	try:
		acc = Account.objects.get(email = uName)
		access = acc.login(pWord, True, meta)
	except Account.DoesNotExist as ex:
		return invalid("Invalid Credentials", False, 200)
	if not access[0]:
		return invalid("Invalid Credentials")
	else:
		request.session.cycle_key()
		request.session['logged_in'] = True
		request.session['token'] = access[1]
		pid = Person.objects.get(email=uName)
		request.session['user'] = pid.name
		request.session['account'] = pid.account.id
		request.session.set_expiry(0)
		D = {
			'success':True
		}
		return JsonResponse(D)

def logout(request):
	if not request.is_ajax():
		D = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)

	member = validate_login(request)	
	if(member):		
		cookie = request.session['token']
		meta = request.META['HTTP_USER_AGENT']
		member.logout(cookie)
		request.session.cycle_key()
		request.session['logged_in'] = False
		request.session['token'] = None
		request.session['user'] = None
		request.session['account'] = None
		request.session.set_expiry(1)
		D = {
			'success':True
		}
		return JsonResponse(D)
	else:
		return invalid("User not logged in",False,401)

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
	return JsonResponse({'success':True, 'result':max})

def validate_login(request):
	if('account' in request.session and 'token' in request.session):
		try:
			acc = Account.objects.get(id = request.session['account'])
			if acc.login_valid(request.session['token']):
				return acc
			else:
				return None
		except Account.ObjectDoesNotExist as ex:
			return None
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
