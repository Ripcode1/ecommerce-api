import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Handles filtering for the product list endpoint.
    
    Usage examples:
        ?min_price=10&max_price=50
        ?category=electronics
        ?in_stock=true
    """
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__slug')
    category_id = django_filters.NumberFilter(field_name='category__id')
    seller = django_filters.NumberFilter(field_name='seller__id')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['category', 'category_id', 'seller', 'is_active']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset.filter(stock_quantity=0)
