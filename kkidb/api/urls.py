"""kki URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin
from kkidb.api import api
from kkidb.api import fileApi

urlpatterns = [
    path("login",api.login),
	path("kettir/<int:id>", api.cat),
	path("kettir",api.cats),
	path("felagar/<int:id>/greidslur",api.payments),
	path("felagar/<int:mid>/greidslur/<slug:gid>",api.payment),
	path("felagar/<int:id>",api.member),
	path("felagar",api.members),
	path("domarar/<int:id>",api.judge),
	path("domarar",api.judges),
	path("folk/<int:id>",api.person),
	path("folk",api.people),
	path("felog/<int:id>",api.organization ),
	path("felog",api.organizations ),
	path("raektanir/<int:id>", api.cattery),
	path("raektanir",api.catteries),
	path("syningar/<int:sid>/keppendur/<int:eid>", api.entrant),
	path("syningar/<int:sid>/keppendur", api.entrants),
	path("syningar/<int:sid>/tilnefningar", api.nominations),
	path("syningar/<int:sid>/tilnefningar/<slug:uri>", api.nomination),
	path("syningar/<int:id>", api.show),
	path("syningar", api.shows),
	path("ems/<slug:breed>/<slug:color>",api.color),
	path("ems/<slug:breed>",api.breed),
	path("ems",api.ems),
	path("stig/<slug:name>-<int:rank>",api.cert),
	path("stig/HP",api.hpCert),
	path("stig",api.certs),
	path("verdlaun/<slug:id>",api.award),
	path("verdlaun",api.awards),
	path("util/skrnr",api.next_regid),
	path("syningar/<int:sid>/skjol/buramidar.pdf",fileApi.test),
	path("syningar/<int:sid>/skjol/urslitablad.pdf",fileApi.finalJudgePaper)
	


#	url("leit",api.find),
#	url("saekja/einstakling",api.get_person),
#	url("saekja/kott",api.get_cat),
#	url("saekja/",api.get),
#	url("skra/greidsla",api.submit_payment),
#	url("skra/einstaklingur",api.submit_person),
#	url("skra/felagi",api.submit_member),
#	url("skra/raektun",api.submit_cattery),
#	url("skra/gelding",api.submit_neuter),
#	url("skra/eigendaskipti",api.submit_ownership_change),
#	url("skra/syning",api.submit_show),
#	url("skra/kottur",api.submit_cat),
#	url("util/skraningarnumer",api.next_regid),
]
