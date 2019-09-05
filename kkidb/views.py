# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from kkidb.auth.authMiddleware import ValidateLogin
from kkidb.models import *
from django.utils.decorators import decorator_from_middleware_with_args
# Create your views here.

isLoggedIn = decorator_from_middleware_with_args(ValidateLogin)


@isLoggedIn()
def index(request):
	template = loader.get_template('index.html')
	context = {}
	return HttpResponse(template.render(context, request))

@isLoggedIn()
def members(request):
	template = loader.get_template("members/members.html")
	members = Person.objects.all().exclude(member__isnull = True).order_by('name')[:25]
	
	context = {'members':members}
	return HttpResponse(template.render(context,request))

@isLoggedIn()
def member_profile(request,id):
	template = loader.get_template("members/member_profile.html")
	member = Member.objects.get(id = id)
	context = {'member':member.person}
	return HttpResponse(template.render(context,request))

@isLoggedIn()
def catteries(request):
	template = loader.get_template("catteries/catteries.html")
	
	context = {}
	return HttpResponse(template.render(context,request))

@isLoggedIn()
def cattery_profile(request,id):
	template = loader.get_template("catteries/cattery_profile.html")
	cattery = Cattery.objects.get(id=id)
	context = {'cattery':cattery}
	return HttpResponse(template.render(context,request))

@isLoggedIn()
def cats(request):
	template = loader.get_template("cats/cats.html")
	
	
	context = {}
	return HttpResponse(template.render(context,request))

@isLoggedIn()
def cat_profile(request,id):
	template = loader.get_template("cats/cat_profile.html")
	cat = Cat.objects.get(id = id)
	litters = cat.litters()
	sibling_litter = cat.litterMates()
	sibling_full = cat.fullSiblings()
	sibling_maternal = cat.maternalSiblings()
	sibling_paternal = cat.paternalSiblings()
	certificates = cat.catcert_set.all()
	certs = [x for x in certificates]
	def sortCert(a):
		score = 0
		if(a.cert.neuter):
			score -= 10000
		return score - a.absRank()

	context = {
		'cat':cat, 
		'litters':litters, 
		'siblings_litter':sibling_litter,
		'siblings_full': sibling_full,
		'siblings_maternal': sibling_maternal,
		'siblings_paternal': sibling_paternal,
		'certs': certs,
	}
	return HttpResponse(template.render(context,request))

@isLoggedIn()
def shows(request):
	template = loader.get_template("shows/shows.html")
	context = {'shows':Show.objects.all().order_by("-date")}

	return HttpResponse(template.render(context,request))

@isLoggedIn()
def show_page(request,show):	
	template = loader.get_template("shows/show_management.html")
	context = {'show':Show.objects.get(id = show)}

	return HttpResponse(template.render(context,request))

@isLoggedIn()
def register_litter(request):	
	template = loader.get_template("cats/cats_register_litter.html")
	context = {'catteries':Cattery.objects.all().order_by("name")}

	return HttpResponse(template.render(context,request))
