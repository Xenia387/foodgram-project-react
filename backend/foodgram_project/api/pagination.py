from django.core import paginator
from rest_framework.pagination import PageNumberPagination

NUMBER: int = 6


class RecipePagination(PageNumberPagination):
    """Пагинация для списка Рецептов."""
    page_size = NUMBER


class CustomPagination(PageNumberPagination):
    """"Пагинация для списка Пользователей."""
    page_size = NUMBER
    page_size_query_param = 'limit'
