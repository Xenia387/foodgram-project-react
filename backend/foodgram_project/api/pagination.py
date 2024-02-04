from rest_framework.pagination import PageNumberPagination

NUMBER: int = 6


class CustomPagination(PageNumberPagination):
    """"Пагинация для списка Пользователей."""
    page_size = NUMBER
    page_size_query_param = 'limit'
