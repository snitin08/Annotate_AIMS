from django.contrib import admin
from django.urls import path, include
from annotate import views

app_name = 'annotate'

urlpatterns = [
    path('',views.annotate,name='annotate'),
]