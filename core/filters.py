import django_filters
from core.models import Visit

class VisitFilter(django_filters.FilterSet):
    hq = django_filters.NumberFilter(field_name='doctor__headquarters')
    sub_hq = django_filters.NumberFilter(field_name='doctor__sub_headquarters')
    mr = django_filters.NumberFilter(field_name='mr')
    doctor = django_filters.NumberFilter(field_name='doctor')
    start_date = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    status = django_filters.CharFilter(field_name='status')

    class Meta:
        model = Visit
        fields = ['hq', 'sub_hq', 'mr', 'doctor', 'start_date', 'end_date', 'status']
