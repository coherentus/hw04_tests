from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class StaticURLTests(TestCase):
    """Проверка доступности статичных страниц."""
    def test_static_pages(self):
        guest_client = Client()
        static_urls = (
            '/about/author/',
            '/about/tech/'
        )
        for url in static_urls:
            with self.subTest(url=url):
                response = guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
