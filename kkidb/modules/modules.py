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

moduleJS = ['/static/shared/modules/js/modules.js']


def payment(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(d)
	
	template = loader.get_template("shared/modules/payment.html")
	context = {}
	d = {}
	d['name'] = 'payment'
	d['html'] = template.render(context,request);
	scripts = moduleJS[:]
	scripts.append("/static/shared/modules/js/payment.js")
	d['js'] = scripts
	return JsonResponse(d)

def member(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(d)
	
	template = loader.get_template("shared/modules/member.html")
	context = {}
	d = {}
	d['name'] = 'member'
	d['html'] = template.render(context,request);
	scripts = moduleJS[:]
	scripts.append("/static/shared/modules/js/payment.js")
	d['js'] = scripts
	return JsonResponse(d)

def person(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(d)
	
	template = loader.get_template("shared/modules/person.html")
	context = {}
	d = {}
	d['name'] = 'person'
	d['html'] = template.render(context,request);
	scripts = moduleJS[:]
	scripts.append("/static/shared/modules/js/person.js")
	d['js'] = scripts
	return JsonResponse(d)