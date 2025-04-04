"""
URL mappings for the user API.
"""
from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('sign-up/', views.CreateUserView.as_view(), name='sign-up'),
]
