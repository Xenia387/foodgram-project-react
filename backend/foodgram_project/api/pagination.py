from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

NUMBER: int = 6


class CustomPagination(PageNumberPagination):
    """"Пагинация."""
    page_size = NUMBER
    page_size_query_param = 'limit'
