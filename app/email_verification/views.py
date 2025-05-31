from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from email_verification.serializers import (
    VerifyEmailSerializer,
    ResendVerificationCodeSerializer,
)

from django.contrib.auth import get_user_model
from django.core.mail import send_mail


class VerifyEmailView(APIView):
    """
    API view to verify email addresses.
    """
    serializer_class = VerifyEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            user = get_user_model().objects.get(
                email=serializer.validated_data['email']
            )
            user.is_verified = True
            user.is_active = True
            user.verification_code = None  # Clear code after use
            user.verification_code_expires = None
            user.save()
            return Response(
                {'detail': 'Email verified successfully'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationCodeView(APIView):
    """
    API view to resend verification code.
    """

    serializer_class = ResendVerificationCodeSerializer

    def get(self, request):
        user = request.user
        if not user:
            return Response(
                {'detail': 'User not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not user.email:
            return Response(
                {'detail': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.is_verified:
            return Response(
                {'detail': 'Email is already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            code = user.generate_verification_code()
            send_mail(
                subject='Welcome to ECommerce App',
                message=(
                    f'Your verification code is: {code}\n'
                    f'It expires in 10 minutes.'
                ),
                from_email='dangbh39@gmail.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response(
                {'detail': 'Verification code resent successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': f'Failed to send verification email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
