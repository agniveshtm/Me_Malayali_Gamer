import django_filters
from .models import Modsinfo
from django_filters import DateFromToRangeFilter,CharFilter,BooleanFilter

class ModsFilter(django_filters.FilterSet):
    type = CharFilter(field_name='type__vehicle_type',lookup_expr='icontains',label='Type')
    category = CharFilter(field_name='category__mod_category',lookup_expr='icontains',label='Category')
    uploaded_on = DateFromToRangeFilter(label='Uploaded Between')
    is_public =  BooleanFilter(label="Public/Private")
    class Meta:
        model = Modsinfo
        fields = ['type','category','uploaded_on','is_public']