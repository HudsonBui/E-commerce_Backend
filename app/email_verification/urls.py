from django.urls import path
from email_verification.views import (
  VerifyEmailView,
  ResendVerificationCodeView,
)

app_name = 'email_verification'

urlpatterns = [
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path(
      'resend-verification-code/',
      ResendVerificationCodeView.as_view(),
      name='resend_verification_code',
    ),
]
