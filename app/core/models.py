"""
Database models.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

import random


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a user with an email, and password."""
        if not email:
            raise ValueError("Users must have an email address.")
        normalized_email = self.normalize_email(email)
        user = self.model(email=normalized_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """Create and return a superuser with an email, and password."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to="user_images", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_expires = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def generate_verification_code(self):
        """Generate a random 6-digit verification code."""
        code = ''.join(random.choices('0123456789', k=6))
        self.verification_code = code
        self.verification_code_expires = \
            timezone.now() \
            + timezone.timedelta(minutes=10)
        self.save()
        return code

    def is_code_valid(self, code):
        """Check if the verification code is valid and not expired."""
        if not self.verification_code or not self.verification_code_expires:
            return False
        if self.verification_code != code:
            return False
        if timezone.now() > self.verification_code_expires:
            return False
        return True


class Category(models.Model):
    """Category of the products."""
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories"
    )
    description = models.TextField(blank=True, null=True)


class Product(models.Model):
    """Product in the system."""
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    description = models.TextField(blank=True, null=True)
    material = models.CharField(max_length=255, blank=True, null=True)
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    weight_unit = models.CharField(
        max_length=10,
        choices=[
            ("kg", "Kilograms"),
            ("g", "Grams"),
            ("lb", "Pounds"),
            ("oz", "Ounces"),
        ],
        default="kg",
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    node_name = models.CharField(max_length=255, blank=True, null=True)


class ProductImage(models.Model):
    """Images for a product."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    url = models.URLField(max_length=500)
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Ensure only one primary image per product."""
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductDetailInformation(models.Model):
    """Product detail in the system."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="detail_information"
    )
    detail_name = models.CharField(max_length=255)
    detail_value = models.TextField(blank=True, null=True)


class ProductDetail(models.Model):
    """Product detail in the system."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_details"
    )
    additional_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    # Detail variant of the product
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)

    stock_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    currency = models.CharField(
        max_length=3,
        choices=[
            ("USD", "US Dollar"),
            ("EUR", "Euro"),
            ("GBP", "British Pound"),
            ("JPY", "Japanese Yen"),
            ("VND", "Vietnamese Dong"),
        ],
        default="USD",
    )


class Order(models.Model):
    """Order of the User."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    order_status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("shipped", "Shipped"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )


class OrderItem(models.Model):
    """Order item in the system."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product_detail = models.ForeignKey(
        ProductDetail,
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )


class Cart(models.Model):
    """Shopping cart of the User."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart"
    )


class CartItem(models.Model):
    """Item in the shopping cart."""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product_detail = models.ForeignKey(
        ProductDetail,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
