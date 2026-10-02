from django.urls import path

from . import views

app_name = 'refy'
urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('<slug:category_slug>/', views.category, name='category'),
    path('<slug:category_slug>/<slug:slug>/', views.section, name='section'),
]