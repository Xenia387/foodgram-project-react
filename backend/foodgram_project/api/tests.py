# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITransactionTestCase
# from rest_framework.authtoken.models import Token

# from users.models import User


# class UserApiTestCase(APITransactionTestCase):

#     @classmethod
#     def setUpClass(cls):
#         cls.username = 'vasya.pupkin'
#         cls.email = 'vpupkin@yandex.ru'
#         cls.password = 'Qwerty123321'
#         super().setUpClass()

#     def test_create_user(self):
#         """Создание пользователя."""
#         url = reverse('users-list')
#         data = {
#             'email': self.email,
#             'username': self.username,
#             'first_name': 'Вася',
#             'last_name': 'Пупкин',
#             'password': self.password
#         }

#         resp = self.client.post(url, data=data)

#         self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(User.objects.filter(email=self.email).exists())

#     def test_get_token(self):
#         """Получение токена."""
#         # Создаем пользователя.
#         user = User.objects.create_user(username=self.username,
#                                         email=self.email,
#                                         password=self.password)
#         url = reverse('login')
#         data = {
#             'email': self.email,
#             'password': self.password,
#         }

#         resp = self.client.post(url, data=data)

#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         auth_token = resp.data.get('auth_token')
#         self.assertEqual(Token.objects.get(user=user).key, auth_token)

#     def test_me(self):
#         user = User.objects.create_user(username=self.username)
#         token = Token.objects.create(user=user)
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
#         url = reverse('users-me')

#         resp = self.client.get(url)

#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         self.assertEqual(resp.data.get('email'), user.email)
