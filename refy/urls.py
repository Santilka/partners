from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import views
from .sitemaps import sitemaps

app_name = 'refy'
urlpatterns = [
    path('', views.home, name='home'),
    path('robots.txt', views.robots, name='robots'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('search/', views.search, name='search'),
    path('go/<int:pk>/', views.go, name='go'),
    path('kursy/<slug:slug>/', views.course_detail, name='course'),
    path('shkoly/<slug:slug>/', views.school_detail, name='school'),
    path('<slug:category_slug>/', views.category, name='category'),
    path('<slug:category_slug>/<slug:slug>/', views.section, name='section'),
]