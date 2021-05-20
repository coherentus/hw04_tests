from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.views import (index, group_index, new_post, profile, post_edit,
                         post_view, group_posts)

User = get_user_model()

class StaticURLTests(TestCase):

    def test_smoke(self):
        """'Дымовой тест. Проверка, что на запрос '/' ответ 200."""
        guest_client = Client()
        
        static_urls = (
            '/',
            '/about/author/',
            '/about/tech/',
        )
        for url in static_urls:
            with url self.subTest(url=url):
                response = guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)