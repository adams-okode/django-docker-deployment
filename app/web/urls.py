from django.contrib import admin
from django.urls import path, include
from web import views

urlpatterns = [
    path('', views.default, name='default'),
    path('home', views.home_page, name='home-page'),
]
