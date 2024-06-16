from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('service/', views.service_view, name='service'),
    path('loading/', views.loading_view, name='loading'),
]
