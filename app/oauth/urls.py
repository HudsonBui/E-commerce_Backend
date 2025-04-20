# api/urls.py
from django.urls import path
from oauth.views import SocialLoginView

urlpatterns = [
    path(
        'auth/<str:backend>/',
        SocialLoginView.as_view(), name='social-login'
    ),
]
