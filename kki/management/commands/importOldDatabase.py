# -*- coding: utf-8 -*-
import csv
import os
from django.core.management.base import BaseCommand, CommandError
from kkidb.models import *
from django.utils import timezone
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from datetime import date
from kkidb.auth import auth
from django.db import transaction
import json

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('File', nargs='+', type=str)
	@transaction.atomic
	def handle(self, *args, **options):
		file = options['File'][0]
		print("Starting pre-import")
		with open(file, 'r') as f:
			dataStore = json.load(f)
		done = 0.0
		lastPerc = 0.05
		length = len(dataStore)
		print("Loaded a datastore of length " + str(length))
		print("Starting seperation into in-memory DB")
		db = {}

		for item in dataStore:
			done += 1
			if ((100*done)/length) > lastPerc:
				#print(str(lastPerc) + "% imported")
				lastPerc += 0.05
			model = item['model'].split(".")[1]
			if model not in db:
				db[model] = []
				#print(model)
			item['fields']['pk'] = item['pk']
			db[model].append(item['fields'])
		
		kkidb = {}
		print("Db seperation finished")

		print("Starting on EMS")
		kkidb['ems'] = {}

		for ems in db['ems']:
			_breed = ems['breed']
			_color = ems['ems']
			_category = ems['category']
			_group = ems['group']

			breedQ = Breed.objects.filter(breed = _breed)
			if(len(breedQ) == 0):
				breed = Breed()
				breed.breed = _breed
				breed.short = _breed
				breed.category = _category
				breed.save()
			else:
				breed = breedQ[0]

			
			colorQ = Color.objects.filter(color = _color)
			if(len(colorQ) == 0):
				color = Color()
				color.color = _color
				color.short = _color
				color.save()
			else:
				color = colorQ[0]

			emsCheck = EMS.objects.filter(breed = breed, color = color)
			if(len(emsCheck) > 0):
				kkidb['ems'][ems['pk']] = emsCheck[0]
				print(color.short + " = " + breed.short + " already exists!")
			else:
				newEms = EMS()
			
			
				newEms.breed = breed
				newEms.color = color
				newEms.group = _group
				newEms.save()
				kkidb['ems'][ems['pk']] = newEms

		print("Done")
		print("Starting on cat_parents")

		
		kkidb['parent'] = {}
		for parent in db['parents']:
			kkidb['parent'][parent['pk']] = parent['cat']

		print("Done")
		print("Starting on cats")
		
		kkidb['cat'] = {}
		for _cat in db['cat']:
			cat = Cat()
			cat.name = _cat['name']
			cat.reg_full = _cat['reg_nr']
			cat.reg_nr = _cat['reg_nr']
			cat.birth_date = _cat['birth']
			cat.reg_date = _cat['registered']
			cat.isMale = not _cat['gender']
			if _cat['dam'] in kkidb['parent']:
				cat.dam = kkidb['cat'][kkidb['parent'][_cat['dam']]]
			else:
				cat.dam = None
			if _cat['sire'] in kkidb['parent']:
				cat.sire = kkidb['cat'][kkidb['parent'][_cat['sire']]]
			else:
				cat.sire = None
			cat.cattery = None
			cat.save()

			kkidb['cat'][_cat['pk']] = cat

		print('Done')
		print("Starting on neutering cats")
		
		kkidb['neuter'] = {}
		for neutered in db['neutered']:
			neuter = Neuter()
			neuter.cat = kkidb['cat'][neutered['catId']]
			neuter.date = neutered['date']
			neuter.save()
			kkidb['neuter'][neutered['pk']] = neuter

		print('Done')
		print("Starting on microchipping cats")
		
		kkidb['microchip'] = {}
		for micro in db['microchip']:
			microchip = Microchip()
			microchip.cat = kkidb['cat'][micro['cat']]
			microchip.microchip = micro['microchip_nr']
			microchip.save()
			kkidb['microchip'][micro['pk']] = microchip

		print('Done')
		print("Starting on color coding cats")
		
		kkidb['catems'] = {}
		for catems in db['cat_ems']:
			entry = CatEms()
			entry.date = catems['reg_date']
			entry.cat = kkidb['cat'][catems['cat']]
			entry.ems = kkidb['ems'][catems['ems']]
			entry.save()
			kkidb['catems'][catems['pk']] = entry


		print('done')
		print('Starting shows')
		
		kkidb['show'] = {}
		for _show in db['show']:
			show = Show()
			show.name = _show['name']
			show.date = _show['date']
			show.location = "Reykjanesbær"
			if(_show['pk'] >= 3):
				per = Person.objects.get(name = 'Helga Karlsdóttir')
			else:
				per = Person.objects.get(name = 'Jósteinn Snorrason')
			show.orginizer = per
			show.save()
			kkidb['show'][_show['pk']] = show 

		
		print('done')
		print('Starting entries')
		
		kkidb['entry'] = {}
		for showentry in db['show_entry']:
			entry = Entry()
			entry.cat = kkidb['cat'][showentry['catId']]
			entry.show = kkidb['show'][showentry['showId']]
			entry.catalog_nr = showentry['cat_show_number']
			entry.guest = False
			entry.save()
			kkidb['entry'][showentry['pk']] = entry

		print('done')
		print('Starting litters')
		
		kkidb['litter'] = {}
		kkidb['littercat'] = {}
		for litterlisting in db['litter']:
			_cat = kkidb['entry'][litterlisting['catId']]
			_show = kkidb['entry'][litterlisting['catId']].show
			_letter = litterlisting['letterId']
			litterQ = Litter.objects.filter(show = _show, catalog = _letter)
			if len(litterQ) == 0:
				litter  = Litter()
				litter.show = _show
				litter.catalog = _letter 
				litter.save()
				kkidb['litter'][litterlisting['pk']] = litter
			else:
				litter = litterQ[0]
			lc = LitterCat()
			lc.litter = litter
			lc.entry = _cat 
			lc.save()
			kkidb['littercat'][litterlisting['pk']] = lc
		
		print("done")
		print("Starting judges")

		kkidb['judge'] = {}
		for j in db['judge']:
			_name = j['name']
			_country = j['country']
			personQ = Person.objects.filter(name = _name)
			if(len(personQ) == 0):
				p = Person()
				p.name = _name 
				p.country = _country 
				p.comment = "Judge"
				p.save()
			else:
				p = personQ[0]
				judgeQ = Judge.objects.filter(person = p)
				if len(judgeQ) > 0:
					kkidb['judge'][j['pk']] = judgeQ[0]
					continue

			judge = Judge()
			judge.person = p
			judge.save()
			kkidb['judge'][j['pk']] = judge 

		print("done")
		print("Starting titles")
		kkidb['title'] = {}

		for c in db['titles']:
			_name = c['name']
			_desc = c['desc']
			_neuter = c['neutered']
			title = Title()
			title.name = _desc
			title.short = _name 
			title.save()
			kkidb['title'][c['pk']] = title


		print("done")
		print("Starting certificates")
		kkidb['cert'] = {}
		for c in db['cert']:
			certname = c['certName']
			certRank = c['certRank']
			neutered = c['neutered']
			title = c['title']
			prev = c['predecessor']
			cert = Cert()
			cert.name = certname
			cert.rank = certRank 
			cert.neuter = neutered
			cert.save()
			if prev in kkidb['cert']:
				kkidb['cert'][prev].next = cert
				kkidb['cert'][prev].save()
			kkidb['cert'][c['pk']] = cert
			if title:
				if title in kkidb['title']:
					kkidb['title'][title].cert = cert
					kkidb['title'][title].save()

		print("done")
		print("Starting judgements")

		kkidb['judgement']= {}
		kkidb['judgementColors'] = {}
		for j in db['judgement']:
			judgement = Judgement()
			judgement.entry = kkidb['entry'][j['entryId']]
			judgement.judge = kkidb['judge'][j['judge']]
			judgement.judgement = j['ex']
			judgement.abs = not j['attendence']
			judgement.biv = j['biv']
			judgement.comment = j['comment']
			judgement.save()
			kkidb['judgementColors'][j['pk']] = kkidb['ems'][j['color']]
			kkidb['judgement'][j['pk']] = judgement
			if j['nom']:
				nom = Nomination()
				nom.judgement = judgement 
				nom.award = Award.objects.all()[0]
				nom.bis = False

		print("done")
		print("Starting cert_judgement")
		kkidb['catcert'] = {}
		for cj in db['cert_judgement']:
			catcert = CatCert()
			catcert.cat = kkidb['cat'][cj['cat']]
			if cj['judgement'] in kkidb['judgement']:
				catcert.judgement = kkidb['judgement'][cj['judgement']]				
				catcert.ems = kkidb['judgementColors'][cj['judgement']]

			catcert.cert = kkidb['cert'][cj['cert']]
			catcert.save()
			kkidb['catcert'][cj['pk']] = catcert

		print("Done")
		print("Starting litter_judgement")
		for lj in db['judgementlitter']:
			litterjudgement = LitterJudgement()
			litterjudgement.show = kkidb['show'][lj['showId']]
			litterjudgement.judge = kkidb['judge'][lj['judge']]
			litterjudgement.abs = not lj['attendence']
			litterjudgement.rank = lj['rank']
			litterjudgement.comment = lj['comment']
			_s = litterjudgement.show
			_letter = lj['litter_nr']

			_l = Litter.objects.filter(show  = _s, catalog = _letter)
			if(len(_l) > 0):
				litterjudgement.litter = _l[0]
			else:
				litterjudgement.litter = None
			litterjudgement.save()

			if lj['nom']:
				litterNom = LitterNomination()
				litterNom.judgement = litterjudgement
				litterNom.award = Award.objects.all()[0]
				litterNom.save()

