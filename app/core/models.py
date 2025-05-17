"""
Database models.
"""
import uuid
import os

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MaxValueValidator

import random


def user_image_file_path(instance, filename):
    """Generate file path for new user image."""
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    return os.path.join("uploads", 'user', filename)


def review_image_file_path(instance, filename):
    """Generate file path for new review image."""
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    return os.path.join("uploads", 'review', filename)


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
    image = models.ImageField(
        upload_to=user_image_file_path,
        blank=True,
        null=True
    )
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
    name = models.CharField(max_length=255, unique=True)
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
    category = models.ManyToManyField(
        Category,
        related_name="products"
    )
    description = models.TextField(blank=True, null=True)
    material = models.CharField(max_length=255, blank=True, null=True)
    weight = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        blank=True,
        null=True
    )
    weight_unit = models.CharField(
        max_length=10,
        null=True,
        blank=True,
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
    style = models.CharField(max_length=255, blank=True, null=True)
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
    # in case that it does not have any variant
    price = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        default=0.00,
        blank=True,
        null=True,
    )
    is_watch = models.BooleanField(default=False)
    review_count_sample = models.PositiveIntegerField(default=0)
    average_rating_sample = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MaxValueValidator(5)],
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MaxValueValidator(5)],
    )
    review_count = models.PositiveIntegerField(default=0)


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


class ProductVariant(models.Model):
    """Product variant combination between colors and sizes.
    Each combination represent product type in the system."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )
    color = models.CharField(max_length=255)
    size = models.TextField(blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)


class ProductDetailInformation(models.Model):
    """Product Detail Information represent Product Detail column
    in Data sample."""
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
    # additional_price = models.DecimalField(
    #     max_digits=10,
    #     decimal_places=2,
    #     default=0.00
    # )

    # Detail variant of the product - Not null but
    # can be empty if the product has no variant
    detail_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="product_variant",
        null=True,
        blank=True
    )

    price = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        default=0.00,
        blank=True,
        null=True,
    )
    sale_price = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        default=0.00,
        blank=True,
        null=True,
    )


class Address(models.Model):
    """User address."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )
    recipient_name = models.CharField(max_length=255)
    recipient_phone_number = models.CharField(max_length=10)
    country = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ("VN", "Vietnam"),
            ("US", "United States"),
            ("JP", "Japan"),
            ("KR", "South Korea"),
            ("CN", "China"),
        ],
        default="US",
    )
    address_line = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    is_default = models.BooleanField(default=False)


class Coupon(models.Model):
    """Coupon for discount."""
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(
        default=0,
        max_digits=5,
        decimal_places=2,
        validators=[MaxValueValidator(100)]
    )
    min_order_amount = models.DecimalField(
        default=0,
        max_digits=100,
        decimal_places=2
    )
    max_discount_amount = models.DecimalField(
        default=0,
        max_digits=100,
        decimal_places=2
    )
    usage_limit = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of times this coupon can be used."
    )
    used_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this coupon has been used."
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)


class Order(models.Model):
    """Order of the User."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True
    )
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        default=0.00
    )
    discount_amount = models.DecimalField(
        max_digits=100,
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
    total_price = models.DecimalField(
        max_digits=100,
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
    update_date = models.DateTimeField(auto_now=True)
    quantity = models.PositiveIntegerField(default=1)


class Review(models.Model):
    """User review about a product"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    product = models.ForeignKey(
        ProductDetail,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.PositiveIntegerField(
        default=1,
        validators=[MaxValueValidator(5)]
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ReviewImage(models.Model):
    """Image for a review."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(
        upload_to=review_image_file_path,
        blank=True,
        null=True
    )


class Payment(models.Model):
    """User Payment for order."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("credit_card", "Credit Card"),
            ("paypal", "PayPal"),
            ("bank_transfer", "Bank Transfer"),
            ("cod", "Cash on Delivery"),
        ],
        default="credit_card",
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
        help_text="Currency of the payment, should match the order's currency."
    )
    amount = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        help_text="Amount paid for the order."
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Transaction ID from Casso (from webhook payload)."
    )
    bank_account_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Bank account ID from Casso (bankSubAccId from webhook)."
    )
    payment_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the payment was confirmed."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the payment record was created."
    )


class Notification(models.Model):
    """Notification for the user."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.TextField()
    type = models.CharField(
        max_length=50,
        choices=[
            ("order", "Order"),
            ("payment", "Payment"),
            ("promotion", "Promotion"),
            ("system", "System"),
        ],
        default="system",
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
