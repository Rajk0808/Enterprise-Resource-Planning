# erp_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('contact/', views.contact, name='contact'),
    path('analysis/', views.analysis, name='analysis'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('interactive_analysis/', views.interactive_analysis, name='interactive_analysis'),
    path('final_report/', views.final_report, name='final_report')
]
