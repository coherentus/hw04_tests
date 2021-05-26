from django.test import Client, TestCase


class URLPathTemplatesTests(TestCase):
    """Проверка правильности шаблонов по url-адресам

    URL                                     temlate
    '/about/author/'                        about/author.html
    '/about/tech/'                          about/tech.html
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_right_temlate_use_with_url(self):
        """Проверка, что по запросу url используется верный шаблон"""
        guest_client = Client()
        array_url_temlate_name = (
            ('/about/author/', 'about/author.html'),
            ('/about/tech/', 'about/tech.html'),
        )

        for page_url_temlat_name in array_url_temlate_name:
            page_url, temlat_name = page_url_temlat_name
            param = ' | '.join([page_url, temlat_name])
            with self.subTest(param=param):
                resp = guest_client.get(page_url)
                self.assertTemplateUsed(resp, temlat_name)
