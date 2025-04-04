"""
Serializers for the user API view.
"""
import re
from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
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
        return get_user_model().objects.create_user(**validated_data)
