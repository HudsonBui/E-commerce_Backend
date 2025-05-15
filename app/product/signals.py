from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from core.models import Review


def update_product_stats(product):
    """Helper function to update product review stats."""
    stats = product.reviews.aggregate(
        count=Count('id'),
        avg_rating=Avg('rating')
    )
    product.review_count = stats['count']
    product.average_rating = round(stats['avg_rating'] or 0.0, 2)
    product.save()


@receiver(post_save, sender=Review)
def update_product_review_stats(sender, instance, created, **kwargs):
    """Update product's stats after a review is saved."""
    update_product_stats(instance.product)


@receiver(post_delete, sender=Review)
def update_product_review_stats_on_delete(sender, instance, **kwargs):
    """Update product's stats after a review is deleted."""
    update_product_stats(instance.product)
