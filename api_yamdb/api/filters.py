from django_filters import rest_framework as filters
from reviews.models import Title


class TitleFilter(filters.FilterSet):
    genre = filters.CharFilter(field_name='genre__slug', lookup_expr='exact')
    category = filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    year = filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'name', 'year']


from api.filters import TitleFilter

class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Произведений."""
    queryset = Title.objects.all()
    # serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names = ['get', 'post', 'delete', "patch"]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter
    # filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer
