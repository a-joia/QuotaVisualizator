from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('service/', views.service_view, name='service'),
    path('loading/', views.loading_view, name='loading'),
    path('suspicious_clusters/', views.suspicious_clusters_view, name='suspicious_clusters'),
    path('get-all-columns-and-values/', views.get_all_columns_and_values, name='get_all_columns_and_values'),
]
