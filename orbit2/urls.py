from django.contrib import admin
from django.urls import path , include
from . import views

urlpatterns = [
    path("login" , views.login , name="login"),
    path("home" , views.home , name="home"),
    path("add_orphan" , views.add_orphan_page , name="add_orphan"),
    path('classify_image/', views.classify_image, name='classify_image')
]