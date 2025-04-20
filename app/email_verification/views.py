from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from email_verification.serializers import VerifyEmailSerializer

from django.contrib.auth import get_user_model


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
