# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
from django.shortcuts import render
from django.template import loader
from django.http import FileResponse
from django.http import QueryDict
from kkidb.auth import auth
from django.core.exceptions import ObjectDoesNotExist
from kkidb.models import *
import math
import json
from datetime import date
from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import  A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from kkidb.api.api import getData


#show 
def test(request,sid):
	if "data" in request.GET:
		data = json.loads(request.GET["data"])
		if "filters" in data:
			settings = data["filters"]
		else:
			settings = {}
	else:
		settings = {}
	show = Show.objects.get(id = sid)
	showDate = show.date
	noms = Nomination.objects.filter(entry__show = show).order_by("award__category","award__ranking","award__name","entry__catalog_nr")
	noms = [x for x in noms]
	if "category_order" in settings:
		noms = sorted(noms,key=lambda s: settings["category_order"].index(s.award.category))
	buffer = io.BytesIO()

	c = canvas.Canvas(buffer, pagesize = A4)    
	width, height = A4 
	off = width * 0.025
	width *= 0.95
	height *= 0.95

	i = 0
	j = 0
	for nom in noms:
		award = nom.award
		entry = nom.entry.catalog_nr
		ems = nom.entry.cat.ems.ems.ems
		if nom.judge:
			judge = nom.judge.person.name
		else:
			judge = "No Judge"
		birthday = nom.entry.cat.birth_date
		months = showDate.month - birthday.month
		years = showDate.year - birthday.year 
		while months < 0:
			months += 12
			years -= 1
		age = str(years)+"y "+str(months)+"m" if years > 0 else str(months)+"m"
		if(excluded(settings,award,nom, show)):
			continue

		left = j*(width/2) + (1+j/2)*off
		bottom = (height/4)*i + (i/2+1)*off
		top = bottom + height/4
		right = left + width / 2
		print("end")
		c.rect(left,bottom,width/2,height/4)
		pdfmetrics.registerFont(TTFont('Calibri', 'fonts/Calibri.ttf'))
		c.setFont("Calibri", 12, leading = None)
		c.drawString(left + off, top - off, award.name)
		c.drawString(left + off, bottom + off, ems)
		c.drawRightString(right - off, bottom + off, judge)
		c.drawRightString(right - off, top - off, age + "/"+ str(birthday))
		c.setFont("Calibri", 40, leading = None)
		c.drawCentredString((left+right)/2, (top+bottom)/2,str(entry))
		j += 1
		if j == 2:
			j = 0
			i += 1
			if i == 4:
				i = 0
				c.showPage()
	c.showPage()  
	c.save()
	buffer.seek(0)
	return FileResponse(buffer, as_attachment=True, filename='buramidar.pdf')

def finalJudgePaper(request, sid):
	if "data" in request.GET:
		data = json.loads(request.GET["data"])
		if "filters" in data:
			settings = data["filters"]
		else:
			settings = {}
	else:
		settings = {}
	show = Show.objects.get(id = sid)
	showDate = show.date
	noms = Nomination.objects.filter(entry__show = show).order_by("award__category","award__ranking","award__name","entry__catalog_nr")
	noms = [x for x in noms]
	if "category_order" in settings:
		noms = sorted(noms,key=lambda s: (settings["category_order"].index(s.award.category), -s.award.ranking))
	buffer = io.BytesIO()
	lastCategory = None
	lastAward = None 
	c = canvas.Canvas(buffer, pagesize = A4)    
	width, height = A4 
	off = width * 0.01
	width *= 0.95
	height *= 0.95
	bigOff = (width / 2)/3
	i = 0
	j = 0
	amount = 100
	baseFont = 10
	pdfmetrics.registerFont(TTFont('Calibri', 'fonts/Calibri.ttf'))
	pdfmetrics.registerFont(TTFont('Calibri_Bold', 'fonts/Calibri_Bold.ttf'))
	for nom in noms:
		award = nom.award
		category = nom.award.category
		entry = nom.entry.catalog_nr
		ems = nom.entry.cat.ems.ems.ems
		if nom.judge:
			judge = nom.judge.person.name
		else:
			judge = "No Judge"
		birthday = nom.entry.cat.birth_date
		months = showDate.month - birthday.month
		years = showDate.year - birthday.year 
		while months < 0:
			months += 12
			years -= 1
		age = str(years)+"y "+str(months)+"m" if years > 0 else str(months)+"m"
		if(excluded(settings,award,nom, show)):
			continue

		left = j*(width/2) + (1+j/2)*off
		bottom = (height/amount)*i + (i/2+1)*off
		top = height - (bottom + height/amount)
		if(not lastCategory or category != lastCategory):
			i +=1 
			left = j*(width/2) + (1+j/2)*off
			bottom = (height/amount)*i + (i/2+1)*off
			top = height - (bottom + height/amount)
			c.setFont("Calibri_Bold", baseFont + 4, leading = None)
			c.drawString(left + off, top - off, category)
			lastCategory = category 
		if(not lastAward or award != lastAward):
			i +=1 
			left = j*(width/2) + (1+j/2)*off
			bottom = (height/amount)*i + (i/2+1)*off
			top = height - (bottom + height/amount)
			c.setFont("Calibri_Bold", baseFont + 2, leading = None)
			c.drawString(left + off, top - off, award.name)
			lastAward = award
			i += 1
			left = j*(width/2) + (1+j/2)*off
			bottom = (height/amount)*i + (i/2+1)*off
			top = height - (bottom + height/amount)
		
		c.setFont("Calibri_Bold", baseFont, leading = None)
		c.drawString(left + 2*off, top - off, str(entry))
		c.setFont("Calibri", baseFont, leading = None)
		c.drawString(left + 5*off, top - off, ems)
		c.drawString(left + 5*off + .75*bigOff, top - off,  age + "/"+ str(birthday))
		c.drawString(left + 5*off + 1.75*bigOff, top - off, judge)

		i += 1
		if i >= 60:
			i = 0
			j +=1
			if j >= 2:
				j = 0
				c.showPage()
	c.showPage()  
	c.save()
	buffer.seek(0)
	return FileResponse(buffer, as_attachment=True, filename='urslitablad.pdf')


def excluded(settings, award, nom, show):
	if "award_categories" in settings:
		if award.category not in settings["award_categories"]:
			return True
	if "judges" in settings:
		if not nom.judge and "null" not in settings["judges"]:
			return True

		if nom.judge and str(nom.judge.id) not in settings["judges"]:
			return True

	if "gender" in settings:
		if nom.entry.cat.isMale and "male" not in settings["gender"]:
			return True

		if not nom.entry.cat.isMale and "female" not in settings["gender"]:
			return True


	if "neutered" in settings:
		if nom.entry.cat.isNeutered and ("true" not in settings["neutered"]):
			return True

		if not nom.entry.cat.isNeutered and ("false" not in settings["neutered"]):
			return True

	if "age" in settings:
		k = nom.entry.cat.isKitten(show.date)
		jun = nom.entry.cat.isJunior(show.date)
		a = not k and not jun
		if k and "kitten" not in settings["age"]:
			return True

		if jun and "junior" not in settings["age"]:
			return True

		if a and "adult" not in settings["age"]:
			return True

	if "catalog_number" in settings:
		if nom.entry.catalog_nr not in settings["catalog_number"]:
			return True
	return False