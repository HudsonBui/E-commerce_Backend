from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from core.models import Cart

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=get_user_model())
def create_user_cart(sender, instance, created, **kwargs):
    """
    Create a cart for the user when a new user is created.
    """
    if created:
        try:
            # Check if the user already has a cart
            if not Cart.objects.filter(user=instance).exists():
                Cart.objects.create(user=instance)
                logger.info(f"Cart created for user: {instance.name}")
            else:
                logger.debug(f"User {instance.name} already has a cart.")
        except IntegrityError as e:
            logger.error(
                f"Database error creating cart for user "
                f"{instance.name}: {str(e)}"
            )
        except Exception as e:
            logger.error(
                f"Unexpected error creating cart for user "
                f"{instance.name}: {str(e)}"
            )
