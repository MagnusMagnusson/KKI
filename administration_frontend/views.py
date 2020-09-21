# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.utils.decorators import decorator_from_middleware_with_args
# Create your views here.

def react_frontend(request):
	template = loader.get_template('administration_frontend.html')
	context = {}
	return HttpResponse(template.render(context, request))
