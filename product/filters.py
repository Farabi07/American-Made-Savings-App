
from django_filters import rest_framework as filters
from product.models import *

class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['name', ]
class SavingsEntryFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = SavingsEntry
        fields = ['name', ]