from django.test import TestCase


class URLPathTemplatesTests(TestCase):
    """Проверка правильности шаблонов по url-адресам."""

    def test_right_temlate_use_with_url(self):
        url_template_name = (
            ('/about/author/', 'about/author.html'),
            ('/about/tech/', 'about/tech.html'),
        )

        for page_url, template_name in url_template_name:
            with self.subTest(url=page_url, temlate=template_name):
                response = self.client.get(page_url)
                self.assertTemplateUsed(response, template_name)
