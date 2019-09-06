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
from kkidb import views
from django.conf.urls import include


urlpatterns = [
    path('api/', include("kkidb.api.urls")),
    path('modules/', include("kkidb.modules.urls")),
    path("",views.index),
    path('kettir/skra/got',views.register_litter),
    path('kettir/<int:id>',views.cat_profile),
    path("kettir",views.cats),
    path('felagar<int:id>',views.member_profile),
    path("felagar",views.members),
    path('raektun/<int:id>',views.cattery_profile),
    path("raektun",views.catteries),
    path('syningar/<int:id>',views.show_page),
    path("syningar",views.shows)
]
