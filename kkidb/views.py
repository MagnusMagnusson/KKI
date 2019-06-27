# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from kkidb.auth import authMiddleWare
from kkidb.models import *
from django.utils.decorators import decorator_from_middleware
# Create your views here.


@decorator_from_middleware(authMiddleWare.ValidateLogin)
def index(request):
	template = loader.get_template('index.html')
	context = {}
	return HttpResponse(template.render(context, request))

@decorator_from_middleware(authMiddleWare.ValidateLogin)
def members(request):
	template = loader.get_template("members/members.html")
	members = Person.objects.all().exclude(member__isnull = True).order_by('name')[:25]
	
	context = {'members':members}
	return HttpResponse(template.render(context,request))