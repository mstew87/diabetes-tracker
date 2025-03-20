from django.urls import path
from . import views

urlpatterns = [
    path('', views.reading_list, name='reading_list'),
    path('<int:pk>/', views.reading_detail, name='reading_detail'),
    path('add/', views.add_reading, name='add_reading'),
    path('<int:pk>/edit/', views.edit_reading, name='edit_reading'),
    path('<int:pk>/delete/', views.delete_reading, name='delete_reading'),
] 