
from django_filters import rest_framework as filters
import django_filters
from product.models import *

class ProductFilter(filters.FilterSet):
    tag = django_filters.CharFilter(field_name='tag')
    store = django_filters.CharFilter(field_name='store')
    category = django_filters.CharFilter(field_name='category')

    class Meta:
        model = Product
        fields = ['tag','store','category']
class SavingsEntryFilter(filters.FilterSet):
    tag = django_filters.CharFilter(field_name='product__tag')
    store = django_filters.CharFilter(field_name='product__store')
    category = django_filters.CharFilter(field_name='product__category')

    class Meta:
        model = SavingsEntry
        fields = ['tag', 'store', 'category']