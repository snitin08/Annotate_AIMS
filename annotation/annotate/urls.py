from django.contrib import admin
from django.urls import path, include
from annotate import views

app_name = 'annotate'

urlpatterns = [
    path('',views.annotate,name='annotate'),
    path('upload_pdf/',views.upload_pdf,name='upload_pdf'),    
]