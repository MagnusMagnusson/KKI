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
	settings = getData(request.body)
	conf_awards = None
	if "awards" in settings:
		conf_awards = settings["awards"]
	show = Show.objects.get(id = sid)
	noms = Nomination.objects.filter(entry__show = show).order_by("award__name", "entry__catalog_nr")
	buffer = io.BytesIO()
	c = canvas.Canvas(buffer, pagesize = A4)    
	width, height = A4 
	off = width * 0.025
	width *= 0.95
	height *= 0.95

	i = 0
	j = 0
	for nom in noms:
		award = nom.award.name
		if conf_awards:
			if award not in conf_awards:
				continue
		entry = nom.entry.catalog_nr
		ems = nom.entry.cat.ems.ems.ems
		if nom.judge:
			judge = nom.judge.person.name
		else:
			judge = "Enginn Dómari"
		left = j*(width/2) + (1+j/2)*off
		bottom = (height/4)*i + (i/2+1)*off
		top = bottom + height/4
		right = left + width / 2
		c.rect(left,bottom,width/2,height/4)
		pdfmetrics.registerFont(TTFont('Calibri', 'fonts/Calibri.ttf'))
		c.setFont("Calibri", 14, leading = None)
		c.drawString(left + off, top - off, ems)
		c.drawRightString(right - off, bottom + off, judge)
		c.drawRightString(right - off, top - off, award)
		c.setFont("Calibri", 32, leading = None)
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