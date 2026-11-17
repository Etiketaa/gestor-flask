from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('organizations/register', csrf_exempt(views.RegisterOrganizationView.as_view()), name='register-organization'),
    path('login', csrf_exempt(views.LoginView.as_view()), name='login'),
    path('logout', csrf_exempt(views.LogoutView.as_view()), name='logout'),
    path('me', csrf_exempt(views.MeView.as_view()), name='me'),
]
