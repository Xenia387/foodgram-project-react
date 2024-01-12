# from django.core import paginator
# from rest_framework.pagination import PageNumberPagination

# NUMBER: int = 6

# # # from django.core.mail import send_mail

# # # from api_yamdb.settings import EMAIL_YAMDB


# # # def send_confirmation_code(email, confirmation_code):
# # #     """Oтправляет код подтверждения для
# # #     подтверждения email-адреса пользователя.
# # #     """
# # #     send_mail(
# # #         subject='Код подтверждения',
# # #         message=f'Код подтверждения: {confirmation_code}',
# # #         from_email=EMAIL_YAMDB,
# # #         recipient_list=(email,),
# # #         fail_silently=False,
# # #     )
# class RecipePagination(PageNumberPagination):
#     page_size = NUMBER


# class UserListPagination(PageNumberPagination):
#     page_size = NUMBER
#     # page_size_query_param = 'limit'


# class CustomPaginator(PageNumberPagination):
#     page_size_query_param = 'limit'

