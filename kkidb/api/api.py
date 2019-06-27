# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import JsonResponse
from kkidb.auth import auth
from kkidb.models import *
from django.contrib.postgres.search import TrigramDistance
# Create your views here.

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

def finna_felaga(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(D)
	name = request.GET['name']
	d = {}
	d['results'] = []
	q = Person.objects.annotate( distance=TrigramDistance('name', name),).filter(distance__lte=0.9).filter(member__isnull = False).order_by('distance')
	for res in q[:25]:
		member = {}
		member['name'] = res.name.encode('utf-8')
		member['ssn'] = res.ssn
		member['email'] = res.email
		member['address'] = res.address
		member['postcode'] = res.postcode
		member['city'] = res.city
		member['id'] = res.member.id

		payment_set = res.member.payment_set;
		payments = []
		payment_set.order_by('date')
		for payment in payment_set.all():
			payments.append(payment)
		if(len(payments) > 0):
			member['last_payment'] =payments[0].date
		
		d['results'].append((res.distance, member))
	d['results'] = list(d['results'])
	return JsonResponse(d)
	

def validate_login(request):
	if('token' in request.session):
		meta = request.META['HTTP_USER_AGENT']
		member = auth.validate_login(request.session['token'],meta)
		return member
	else:
		return None