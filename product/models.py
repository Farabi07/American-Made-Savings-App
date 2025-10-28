from django.db import models
from django.conf import settings
class Tag(models.TextChoices):
    AMERICAN_MADE = 'AM', 'American Made'
    TARIFF_FREE = 'TF', 'Tariff Free'
    AUS_T = 'AUS-T', 'Assembled in USA but Tariffed'
    BOTH = 'Both', 'Both'
    NONE = 'None', 'None'
class Product(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    store = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    affiliate_url = models.URLField(blank=True, null=True)
    tag = models.CharField(max_length=10, choices=Tag.choices, default=Tag.NONE)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="created_products", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="updated_products", null=True, blank=True)
    class Meta:
        ordering = ('-id',)
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name


class SavingsEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="savings_entries")
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    affiliate_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    savings = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_saved = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="created_savings_entries", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="updated_savings_entries", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.savings:
            self.savings = self.regular_price - self.affiliate_price
        super(SavingsEntry, self).save(*args, **kwargs)
    def __str__(self):
        return f"Savings on {self.product.name} - ${self.savings:.2f}"
    
class AnalyticsEvent(models.Model):
    EVENT_TYPES = (
        ('store_click', 'Store Click'),
        ('list_create', 'List Create'),
        ('list_reorder', 'List Reorder'),
        ('savings_add', 'Savings Add'),
        ('paywall_view', 'Paywall View'),
        ('subscribe_success', 'Subscribe Success'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]