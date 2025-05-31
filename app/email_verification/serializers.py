"""
Serializers for the email verification app.
"""
from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('verification_code')
        try:
            user = get_user_model().objects.get(email=email)
            if user.is_verified:
                raise serializers.ValidationError(
                    _('Email is already verified.')
                )
            if not user.is_code_valid(code):
                raise serializers.ValidationError(
                    _('Invalid verification code.')
                )
            return attrs
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError(
                _('User with this email does not exist.')
            )


class ResendVerificationCodeSerializer(serializers.Serializer):
    """Serializer for resending verification code."""
    pass
