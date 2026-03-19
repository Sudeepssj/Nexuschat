from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<slug:slug>/', views.room, name='room'),
    path('create-room/', views.create_room, name='create_room'),
    path('dm/<int:user_id>/', views.direct_message, name='direct_message'),
    path('search/', views.search, name='search'),
    path('notifications/', views.notifications, name='notifications'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('register/', views.register, name='register'),
]
