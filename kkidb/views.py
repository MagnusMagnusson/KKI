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

@decorator_from_middleware(authMiddleWare.ValidateLogin)
def member_profile(request,id):
	template = loader.get_template("members/member_profile.html")
	member = Member.objects.get(id = id)
	context = {'member':member.person}
	return HttpResponse(template.render(context,request))

@decorator_from_middleware(authMiddleWare.ValidateLogin)
def catteries(request):
	template = loader.get_template("catteries/catteries.html")
	
	context = {}
	return HttpResponse(template.render(context,request))

@decorator_from_middleware(authMiddleWare.ValidateLogin)
def cattery_profile(request,id):
	template = loader.get_template("catteries/cattery_profile.html")
	cattery = Cattery.objects.get(id=id)
	context = {'cattery':cattery}
	return HttpResponse(template.render(context,request))

@decorator_from_middleware(authMiddleWare.ValidateLogin)
def cats(request):
	template = loader.get_template("cats/cats.html")
	
	
	context = {}
	return HttpResponse(template.render(context,request))

@decorator_from_middleware(authMiddleWare.ValidateLogin)
def cat_profile(request,id):
	template = loader.get_template("cats/cat_profile.html")
	cat = Cat.objects.get(id = id)
	context = {'cat':cat}
	return HttpResponse(template.render(context,request))
