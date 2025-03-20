from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('trends/', views.trends, name='trends'),
    path('reports/', views.reports, name='reports'),
    path('prediction/', views.prediction, name='prediction'),
] 