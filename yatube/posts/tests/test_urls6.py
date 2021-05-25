from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import response
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


User = get_user_model()


class ReturnErrorPagesTests(TestCase):

    def test_404(self):
        """Проверка, что на запрос несуществующей страницы ответ 404."""
        guest_client = Client()
        static_url = ('/very/wrong/url/path/')
        response = guest_client.get(static_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
