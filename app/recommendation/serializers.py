from rest_framework import serializers
from core.models import UserAction


class UserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = [
            'id',
            'user_id',
            'product_id',
            'event_type',
            'event_time',
            'score'
        ]
        read_only_fields = ['id', 'event_time']

    def validate_event_type(self, value):
        valid_event_types = [
            'view',
            'cart',
            'purchase',
            'remove_from_cart']
        if value not in valid_event_types:
            raise serializers.ValidationError(
                "Invalid event type. "
                f"Must be one of {valid_event_types}."
            )
        return value
