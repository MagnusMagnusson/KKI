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
from kkidb import views
from django.conf.urls import include


urlpatterns = [
    url(r'api/', include("kkidb.api.urls")),
    url(r'modules/', include("kkidb.modules.urls")),
    url(r"^$",views.index),
    url(r'kettir/skra/got',views.register_litter),
    url(r'kettir/([0-9]*)',views.cat_profile),
    url("kettir",views.cats),
    url(r'felagar/([0-9]{6})',views.member_profile),
    url("felagar",views.members),
    url(r'raektun/([0-9]*)',views.cattery_profile),
    url("raektun",views.catteries),
    url(r'syningar/([0-9]*)',views.show_page),
    url("syningar",views.shows)
]
