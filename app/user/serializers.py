"""
Serializers for the user API view.
"""
import re
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.core.mail import send_mail
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""
    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'password',
            'name',
            'address',
            'phone_number',
            'birthday',
            'image',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 14}
        }

    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                'Password must contain at least one uppercase letter.'
            )
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError(
                'Password must contain at least one lowercase letter.'
            )
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError(
                'Password must contain at least one digit.'
            )
        if not re.search(r'[~`!@#$%^&* ()-_+= {} []|\;:"<>,./?]', value):
            raise serializers.ValidationError(
                'Password must contain at least one special character.'
            )
        return value

    def create(self, validated_data):
        """Create a user with encrypted password and return it."""
        user = get_user_model().objects.create_user(**validated_data)
        user.is_verified = False
        code = user.generate_verification_code()
        send_mail(
            subject='Welcome to ECommerce App',
            message=(
                f'Your verification code is: {code}\n'
                f'It expires in 10 minutes.'
            ),
            from_email='hudsonbui369vn@gmail.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        return user

    def update(self, instance, validated_data):
        """update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images."""

    image = serializers.ImageField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'name', 'image')
        read_only_fields = ('id', 'name')


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and athenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
