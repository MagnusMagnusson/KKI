# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import JsonResponse
from kkidb.auth import auth
from kkidb.models import *
from django import template

from django.contrib.postgres.search import TrigramDistance
# Create your views here.

moduleJS = ['/static/shared/modules/js/modules.js']

def getModule(request, module):
	if not request.is_ajax():
		return invalid("Ajax required",True,400)
	try:
		template = loader.get_template("shared/modules/"+module+".html")
		context = {}
		d = {}
		d['name'] = module
		d['html'] = template.render(context,request);
		scripts = moduleJS[:]
		scripts.append("/static/shared/modules/js/"+module+".js")
		d['js'] = scripts
	except Exception as ex:
		return invalid("No module by name "+module,True,404)
	return JsonResponse(d)



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