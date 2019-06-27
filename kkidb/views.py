# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from kkidb.auth import authMiddleWare
from django.utils.decorators import decorator_from_middleware
# Create your views here.


@decorator_from_middleware(authMiddleWare.ValidateLogin)
def index(request):
	template = loader.get_template('index.html')
	context = {}
	return HttpResponse(template.render(context, request))


