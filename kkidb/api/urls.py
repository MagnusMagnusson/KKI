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
from django.conf.urls import url
from django.contrib import admin
from kkidb.api import api

urlpatterns = [
    url("login",api.login),
	url("leit",api.find),
	url("saekja/einstakling",api.get_person),
	url("saekja/kott",api.get_cat),
	url("saekja/",api.get),
	url("skra/greidsla",api.submit_payment),
	url("skra/einstaklingur",api.submit_person),
	url("skra/felagi",api.submit_member),
	url("skra/raektun",api.submit_cattery),
	url("skra/gelding",api.submit_neuter),
	url("skra/eigendaskipti",api.submit_ownership_change),
	url("skra/syning",api.submit_show),
	url("skra/kottur",api.submit_cat),
	url("util/skraningarnumer",api.next_regid),
]
