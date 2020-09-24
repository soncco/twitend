from django.urls import path, include

from rest_framework import routers

from front import views

app_name = 'front'
urlpatterns = [
    path('search/', views.search, name='search'),
    path('trend/<str:hashtag>', views.trend, name='trend'),
    path('', views.index, name='index'),
    path('<str:location>/', views.index, name='index'),
    path('<str:location>/<str:when>/', views.index, name='index'),
    path('<str:location>/<str:when>/<int:hour>/', views.index, name='index'),
    
    #path('stats/<str:hashtag>/<str:location>/<str:date>/<int:hour>/', views.trend_stats, name='trend_stats'),
]
