from django.urls import path
from . import views

urlpatterns = [
    path('organizations/register', views.RegisterOrganizationView.as_view(), name='register-organization'),
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('auth/logout', views.LogoutView.as_view(), name='logout'),
    path('auth/me', views.MeView.as_view(), name='me'),
]
