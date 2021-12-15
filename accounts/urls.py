from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.register,name='register'),
    path('login/', views.login,name='login'),
    path('logout/', views.logout,name='logout'),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('', views.dashboard,name='dashboard'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgot_password/', views.forgot_password,name='forgot_password'),
    path('reset_password_validation/<uidb64>/<token>/', views.reset_password_validation, name='reset_password_validation'),
    path('reset_password/', views.reset_password,name='reset_password'),
]
