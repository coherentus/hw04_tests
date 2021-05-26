from django.test import Client, TestCase


class URLPathTemplatesTests(TestCase):
    """Проверка правильности шаблонов по url-адресам."""

    def test_right_temlate_use_with_url(self):
        """Проверка, что по запросу url используется верный шаблон."""
        url_template_name = (
            ('/about/author/', 'about/author.html'),
            ('/about/tech/', 'about/tech.html'),
        )

        for page_url, template_name in url_template_name:
            with self.subTest(url=page_url, temlate=template_name):
                resp = self.client.get(page_url)
                self.assertTemplateUsed(resp, template_name)
