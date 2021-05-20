def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/author/.

        Для страницы 'about/author' должен применяться
        шаблон 'about/author.html'"""
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(
            response, 'about/author.html',
            ('Нужно проверить, что для страницы "/about/author"'
             ' используется шаблон "about/author.html"')
        )

    def test_tech_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/tech/.

        Для страницы '/about/tech' должен применяться
        шаблон 'about/tech.html'"""
        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(
            response, 'about/tech.html',
            ('Нужно проверить, что для страницы "/about/tech"'
             ' используется шаблон "about/tech.html"')
        )
