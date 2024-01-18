from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("login_view", views.login_view, name="login_view"),
    path("home", views.home, name="home"),
    path("add_orphan", views.add_orphan_page, name="add_orphan"),
    path('classify_image/', views.classify_image, name='classify_image'),
    path('logout', views.logout_view, name="logout"),
    path("add_pendency", views.add_pendency, name="add_pendency"),
    path('search' , views.search_view , name='search'),
    path('get_brands_for_vertical/', views.get_brands_for_vertical, name='get_brands_for_vertical'),
    path('results/', views.results_view, name='results'),
    path('get_details/<str:tid>/', views.get_details, name='get_details')

]


