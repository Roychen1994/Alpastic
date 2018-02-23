"""HdShop URL Configuration

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
from HdWxShop import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', views.index),
    url(r'^mainnews/(\w+)?$',views.mainnews),
    url(r'^news/(\w+)$',views.news),
    url(r'^login/$',views.login),
    url(r'^register/user/$',views.Registeruser),
    url(r'^register/user/usercheck/$',views.check_user),
    url(r'^create_code_img/$',views.create_code_img),
    url(r'logout/$',views.logout),
    url(r'^shop/$',views.hdshop),
    url(r'test/$',views.testviews),
]


