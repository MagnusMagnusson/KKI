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
	scripts.append("/static/shared/modules/js/member.js")
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

def cattery(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(d)
	
	template = loader.get_template("shared/modules/cattery.html")
	orgs = Organization.objects.all()
	context = {
		'orgs':orgs
	}
	d = {}
	d['name'] = 'cattery'
	d['html'] = template.render(context,request);
	scripts = moduleJS[:]
	scripts.append("/static/shared/modules/js/cattery.js")
	d['js'] = scripts
	return JsonResponse(d)

def catteryOwner(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(d)
	
	template = loader.get_template("shared/modules/catteryOwner.html")
	
	d = {}
	context = {}
	d['name'] = 'catteryOwner'
	d['html'] = template.render(context,request);
	scripts = moduleJS[:]
	scripts.append("/static/shared/modules/js/catteryOwner.js")
	d['js'] = scripts
	return JsonResponse(d)

def catNeuter(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(d)
	
	template = loader.get_template("shared/modules/catNeuter.html")
	
	d = {}
	context = {}
	d['name'] = 'catNeuter'
	d['html'] = template.render(context,request);
	scripts = moduleJS[:]
	scripts.append("/static/shared/modules/js/catNeuter.js")
	d['js'] = scripts
	return JsonResponse(d)

def catOwner(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(d)
	
	template = loader.get_template("shared/modules/catOwner.html")
	
	d = {}
	context = {}
	d['name'] = 'catOwner'
	d['html'] = template.render(context,request);
	scripts = moduleJS[:]
	scripts.append("/static/shared/modules/js/catOwner.js")
	d['js'] = scripts
	return JsonResponse(d)

def show(request):
	if not request.is_ajax():
		d = {
			'success':False,
			'error': "óvænt villa kom upp við beiðni þinni"
		}
		return JsonResponse(d)
	
	template = loader.get_template("shared/modules/show.html")
	
	d = {}
	context = {}
	d['name'] = 'show'
	d['html'] = template.render(context,request);
	scripts = moduleJS[:]
	scripts.append("/static/shared/modules/js/show.js")
	d['js'] = scripts
	return JsonResponse(d)