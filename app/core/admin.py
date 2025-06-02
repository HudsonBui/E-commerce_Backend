"""Django admin customizations."""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from django.shortcuts import render
from django.http import HttpResponseRedirect

from core import models
from core.forms import BroadcastNotificationForm


class UserAdmin(BaseUserAdmin):
    """Define admin pages for users."""
    ordering = ['id']
    list_display = [
        'email',
        'name',
        'phone_number',
        'address',
        'is_verified',
        'is_active',
        'gender',
    ]
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Personal Info'), {
            'fields': (
                'name',
                'phone_number',
                'address',
                'gender'
                )
            }),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ('last_login',)
    add_fieldsets = (
        (None, {
            'classes': ('wide', 'extrapretty'),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'phone_number',
                'address',
                'gender',
                'is_active',
                'is_staff',
                'is_verified',
                'is_superuser',
            ),
        }),
    )


class CategoryAdmin(admin.ModelAdmin):
    """Define admin pages for categories."""
    list_display = ('name', 'parent_category_name', 'description')
    search_fields = ('name',)
    ordering = ['-id']
    fieldsets = (
        (None, {'fields': ('name', 'parent_category', 'description')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide', 'extrapretty'),
            'fields': (
                'name',
                'parent_category',
                'description'
            ),
        }),
    )

    list_filter = ('parent_category',)

    def parent_category_name(self, obj):
        """Return parent category name or empty string if None."""
        if obj.parent_category:
            return obj.parent_category.name
        return '-'
    parent_category_name.short_description = 'Parent Category'


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""
    model = models.ProductImage
    extra = 1  # Number of empty forms to display
    fields = ('url', 'is_primary')
    readonly_fields = ()


class ProductVariantAdmin(admin.ModelAdmin):
    search_fields = ['color', 'size', 'product__name']
    list_display = ['product', 'color', 'size', 'stock_quantity']


class ProductDetailInline(admin.TabularInline):
    """Inline admin for product details."""
    model = models.ProductDetail
    extra = 1
    fields = ('detail_variant', 'price', 'sale_price')
    autocomplete_fields = ['detail_variant']


class ProductDetailInformationInline(admin.TabularInline):
    """Inline admin for product detail information."""
    model = models.ProductDetailInformation
    extra = 1
    fields = ('detail_name', 'detail_value')


class ProductAdmin(admin.ModelAdmin):
    """Define admin pages for products."""
    list_display = [
        'name',
        'price',
        'stock_quantity',
        'average_rating',
        'currency'
    ]
    search_fields = [
        'name',
        'category__name',
        'description',
        'material',
        'style'
    ]
    list_filter = ['category__name', 'currency']
    ordering = ['-id']
    list_per_page = 20

    fieldsets = (
        (None, {'fields': ('name', 'category', 'price', 'currency')}),
        (_('Details'), {
            'fields': (
                'description',
                'material',
                'weight',
                'weight_unit',
                'style'
            )}),
        (_('Stock'), {'fields': ('stock_quantity',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide', 'extrapretty'),
            'fields': (
                'name',
                'category__name',
                'price',
                'currency',
                'description',
                'material',
                'weight',
                'weight_unit',
                'style',
                'stock_quantity',
            ),
        })
    )

    inlines = [
        ProductImageInline,
        ProductDetailInline,
        ProductDetailInformationInline,
    ]

    readonly_fields = ('average_rating', 'review_count')
    filter_horizontal = ('category',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related(
            'category',  # For ManyToManyField
            'images',   # For ProductImageInline
            'product_details',  # For ProductDetailInline
            'detail_information',  # For ProductDetailInformationInline
            'product_details__detail_variant'
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = models.Category.objects.select_related(
                'parent_category'
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class NotificationAdminForm(forms.ModelForm):
    """Custom form for NotificationAdmin with a broadcast option."""
    send_to_all_users = forms.BooleanField(
        label="Send to all users",
        required=False,
        initial=False,
    )

    class Meta:
        model = models.Notification
        fields = '__all__'


class NotificationAdmin(admin.ModelAdmin):
    """Define admin pages for notifications."""
    list_display = [
        'user',
        'type',
        'is_read',
        'created_at',
        'title',
        'short_message'
    ]
    search_fields = [
        'user__email',
        'user__name',
        'message',
        'title',
    ]
    list_filter = ['type', 'is_read', 'created_at']
    ordering = ['-created_at']
    form = NotificationAdminForm

    add_fieldsets = (
        (None, {
            'classes': ('wide', 'extrapretty'),
            'fields': (
                'user',
                'type',
                'title',
                'message',
                'is_read',
                'send_to_all_users',
            ),
        }),
    )

    fieldsets = (
        (None, {'fields': ('user', 'type')}),
        (_('Content'), {'fields': ('title', 'message',)}),
        (_('Broadcast'), {'fields': ('send_to_all_users',)}),
    )

    list_select_related = ('user',)

    readonly_fields = ('created_at',)

    def short_message(self, obj):
        """Return truncated message for display in list view."""
        return obj.message[:50] + '...' if len(
            obj.message
        ) > 50 else obj.message
    short_message.short_description = 'Message'

    def add_view(self, request, form_url='', extra_context=None):
        """Override add_view to handle broadcasting to all users."""
        if request.method == 'POST':
            form = self.form(request.POST)
            if form.is_valid():
                send_to_all_users = form.cleaned_data['send_to_all_users']
                if send_to_all_users:
                    # Broadcast to all users
                    users = models.User.objects.all()
                    notifications = [
                        models.Notification(
                            user=user,
                            type=form.cleaned_data['type'],
                            title=form.cleaned_data['title'],
                            message=form.cleaned_data['message'],
                            is_read=form.cleaned_data['is_read'],
                        )
                        for user in users
                    ]
                    models.Notification.objects.bulk_create(notifications)
                    self.message_user(
                        request,
                        f"Successfully created {len(notifications)}" +
                        "notifications for all users."
                    )
                    return HttpResponseRedirect('../')
                else:
                    # Save a single notification as usual
                    return super().add_view(request, form_url, extra_context)
        return super().add_view(request, form_url, extra_context)

    actions = ['broadcast_notification']

    def broadcast_notification(self, request, queryset=None):
        """Action to create a notification for all users."""
        if 'apply' in request.POST:
            form = BroadcastNotificationForm(request.POST)
            if form.is_valid():
                users = models.User.objects.all()
                if not users.exists():
                    self.message_user(
                        request,
                        "No users found to send notifications to.",
                        level='error'
                    )
                    return HttpResponseRedirect(request.get_full_path())
                try:
                    notifications = [
                        models.Notification(
                            user=user,
                            type=form.cleaned_data['type'],
                            title=form.cleaned_data['title'],
                            message=form.cleaned_data['message'],
                            is_read=form.cleaned_data['is_read'],
                        )
                        for user in users
                    ]
                    models.Notification.objects.bulk_create(notifications)
                    self.message_user(
                        request,
                        f"Successfully created {len(notifications)}" +
                        " notifications for all users."
                    )
                except Exception as e:
                    self.message_user(
                        request,
                        f"Failed to create notifications: {str(e)}",
                        level='error'
                    )
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = BroadcastNotificationForm()
        return render(
            request,
            'admin/broadcast_notification_form.html',
            {'form': form, 'title': 'Send Notification to All Users'}
        )

    broadcast_notification.short_description = "Send notification to all users"


class CouponAdmin(admin.ModelAdmin):
    """Define admin pages for coupons."""
    list_display = [
        'code',
        'discount_percentage',
        'min_order_amount',
        'max_discount_amount',
        'start_date',
        'end_date',
        'used_count',
        'is_active',
    ]
    search_fields = ['code']
    list_filter = ['is_active', 'start_date', 'end_date']
    ordering = ['-start_date']

    add_fieldsets = (
        (None, {
            'classes': ('wide', 'extrapretty'),
            'fields': (
                'code',
                'discount_percentage',
                'min_order_amount',
                'max_discount_amount',
                'start_date',
                'end_date',
                'usage_limit',
                'is_active'
            ),
        }),
    )

    fieldsets = (
        (None, {'fields': ('code', 'is_active')}),
        (_('Discount Info'), {
            'fields': (
                'discount_percentage',
                'min_order_amount',
                'max_discount_amount'
            )}),
        (_('Usage Limits'), {
            'fields': (
                'usage_limit',
                'used_count'
            )}),
        (_('Validity Period'), {
            'fields': (
                'start_date',
                'end_date'
            )}),
    )

    readonly_fields = ('used_count',)


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = models.OrderItem
    extra = 1  # Number of empty forms to display
    fields = ('product_detail', 'quantity', 'total_price')
    readonly_fields = ('product_detail', 'total_price')

    def total_price(self, obj):
        """Calculate total price for the order item."""
        return obj.quantity * obj.product_detail.sale_price
    total_price.short_description = 'Total Price'


class OrderAdmin(admin.ModelAdmin):
    """Define admin pages for orders."""
    list_display = [
        'user',
        'address',
        'coupon',
        'order_date',
        'total_amount',
        'discount_amount',
        'order_status'
    ]
    search_fields = ['user__email', 'coupon__code', 'id']
    list_filter = ['order_status', 'order_date', 'coupon']
    ordering = ['-order_date']
    inlines = [OrderItemInline]


class ReviewAdmin(admin.ModelAdmin):
    """Define admin pages for reviews."""
    list_display = [
        'user',
        'product',
        'rating',
        'title',
        'content',
        'created_at',
    ]
    search_fields = ['user__email', 'product__name', 'comment']
    list_filter = ['rating', 'created_at']
    ordering = ['-created_at']

    def content(self, obj):
        """Return truncated comment for display in list view."""
        if len(obj.comment) > 50:
            return obj.comment[:50] + '...'
        else:
            return obj.comment
    content.short_description = 'Comment'


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Notification, NotificationAdmin)
admin.site.register(models.Coupon, CouponAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.Review, ReviewAdmin)
admin.site.register(models.ProductVariant, ProductVariantAdmin)
