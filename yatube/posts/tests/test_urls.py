from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.views import (index, group_index, new_post, profile, post_edit,
                         post_view, group_posts)

User = get_user_model()


class YaTbStaticPagesURLTests(TestCase):
    """Проверка статичных страниц 'об авторе' 'о технолоиях'."""
    def setUp(self):
        # Неавторизованый клиент
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/author/."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(
            response.status_code, 200,
            ('Нужно проверить доступность страницы /about/author'
             'для неавторизованного пользователя')
        )

    def test_tech_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/tech/."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(
            response.status_code, 200,
            ('Нужно проверить доступность страницы /about/tech'
             ' для неавторизованного пользователя')
        )

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


class YatubeURL_AbsPath_Tests(TestCase):
    """Проверка доступности абсолютных url-адресов

    В проекте есть адреса с разной доступностью для guest и user
    URL                      тип пользователя             редирект
    "/"                                     g
    "/group/"                               g
    "/group/<slug:slug>/"                   g
    "/<str:username>/"                      g
    "/<str:username>/<int:post_id>/"        g
    "/<str:username>/<int:post_id>/edit/"   u-a     g->/login
                                                    u->/username/post_id/
    "/new/"                                 u       g->/login
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # два тестовых юзера, один - автор поста
        cls.user_with_post = User.objects.create(
            username='poster'
        )
        cls.user_no_post = User.objects.create(
            username='silent'
        )
        # тестовая группа
        cls.group_test = Group.objects.create(
            title='test_group_title',
            slug='test-slug'
        )

        # тестовый пост
        cls.test_post = Post.objects.create(
            author=cls.user_with_post,
            text='test_post_text'
        )
        cls.test_post.save()
        cls.group_test.save()

        # неавторизованный клиент
        cls.guest_client = Client()
        # авторизованный клиент с постом
        cls.authorized_client_a = Client()
        cls.authorized_client_a.force_login(cls.user_with_post)
        # авторизованный клиент без поста
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_no_post)

        # набор пар "url": "status code" для guest
        cls.templts_pgs_names = {
            '/': 200,
            '/group/': 200,
            '/group/test-slug/': 200,
            '/poster/': 200,
            '/poster/1/': 200
        }

    def setUp(self):
        self.test_class = YatubeURL_AbsPath_Tests

    def test_guest_get_nonautorized_pages(self):
        """Проверка, что guest видит доступные страницы"""
        for page_url, resp_code in self.test_class.templts_pgs_names.items():

            with self.subTest(page_url=page_url):
                resp = self.test_class.guest_client.get(page_url)
                self.assertEqual(resp.status_code, resp_code, page_url)

    # проверка редиректов по абсолютным путям
    # guest "new/" -> "login/"
    # method == GET
    def test_guest_abs_new_redirect_login_get(self):
        """Проверка, что guest GET /new -> /auth/login/?next=/new/"""
        resp = self.test_class.guest_client.get('/new/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/auth/login/?next=/new/')

    # method == POST
    def test_guest_abs_new_redirect_login_post(self):
        """Проверка, что guest POST /new -> /auth/login/?next=/new/"""
        resp = self.test_class.guest_client.post('/new/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/auth/login/?next=/new/')

    # guest GET "<username>/post_id/edit" -> "login/"
    def test_guest_abs_edit_redirect_login_get(self):
        """Проверка, что guest GET /user/post/edit -> /auth/login/?next=..."""
        resp = self.test_class.guest_client.get('/poster/1/edit/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/auth/login/?next=/poster/1/edit/')

    # guest POST "<username>/post_id/edit" -> "login/"
    def test_guest_abs_edit_redirect_login_post(self):
        """Проверка, что guest POST /user/post/edit -> /auth/login/?next=..."""
        resp = self.test_class.guest_client.post('/poster/1/edit/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/auth/login/?next=/poster/1/edit/')

    # user-not-author "<username>/post_id/edit" -> "<username>/post_id/"
    # method == GET
    def test_user_abs_edit_redirect_postcard_get(self):
        """Проверка, что не автор GET /user/post/edit -> /user/post/"""
        resp = self.test_class.authorized_client.get('/poster/1/edit/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/poster/1/')

    # method == POST
    def test_user_abs_edit_redirect_postcard_post(self):
        """Проверка, что не автор POST /user/post/edit -> /user/post/"""
        resp = self.test_class.authorized_client.post('/poster/1/edit/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/poster/1/')

    # user-author "<username>/post_id/edit" 200
    # method == GET
    def test_user_author_abs_edit_redirect_postcard_get(self):
        """Проверка, что автор GET /user/post/edit == status 200"""
        resp = self.test_class.authorized_client_a.get('/poster/1/edit/')
        self.assertEqual(resp.status_code, 200)

    # method == POST
    def test_user_author_abs_edit_redirect_postcard_post(self):
        """Проверка, что автор POST /user/post/edit == status 200"""
        resp = self.test_class.authorized_client_a.post('/poster/1/edit/')
        self.assertEqual(resp.status_code, 200)


class YatubeURL_Path_Tests_reverse(TestCase):
    """Проверка доступности url-адресов через reverse()

    URL                                     view                name
    '/'                                     views.index         'index'
    '/group/'                               views.group_index   'group_index'
    '/group/<slug:slug>/'                   views.group_posts   'group'
    '/new/'                                 views.new_post      'new_post'
    '<str:username>/'                       views.profile       'profile'
    '<str:username>/<int:post_id>/'         views.post_view     'name='post'
    '<str:username>/<int:post_id>/edit/'    views.post_edit     'post_edit'
    '/signup/'                           views.SignUp.as_view() 'signup'
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # два тестовых юзера, один - автор поста
        cls.user_with_post = User.objects.create(
            username='poster_user'
        )
        cls.user_no_post = User.objects.create(
            username='silent_user'
        )
        # тестовая группа
        cls.group_test = Group.objects.create(
            title='test_group_title',
            slug='test-slug'
        )

        # тестовый пост
        cls.test_post = Post.objects.create(
            author=cls.user_with_post,
            text='test_post_text'
        )
        cls.test_post.save()
        cls.group_test.save()

        # неавторизованный клиент
        cls.guest_client = Client()
        # авторизованный клиент с постом
        cls.authorized_client_a = Client()
        cls.authorized_client_a.force_login(cls.user_with_post)
        # авторизованный клиент без поста
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_no_post)

        # набор пар "returned reverse url": ("views_name", "name")
        cls.templts_pgs_names_simple = {
            '/': (index, 'index'),
            '/group/': (group_index, 'group_index'),
            '/new/': (new_post, 'new_post'),
        }

        # набор пар "returned reverse url": ("views_name", "name", kwargs)
        cls.templts_pgs_names_args = {
            '/group/test-slug/': (group_posts, 'group',
                                  {'slug': cls.group_test.slug}),
            '/poster_user/': (profile, 'profile',
                              {'username': cls.user_with_post.username}),
            '/poster_user/1/': (post_view, 'post',
                                {'username': cls.user_with_post.username,
                                 'post_id': cls.test_post.id}),
            '/poster_user/1/edit/': (post_edit, 'post_edit',
                                     {'username': cls.user_with_post.username,
                                      'post_id': cls.test_post.id}),
        }

    def test_reverse_url_simple(self):
        """Проверка, что reverse() отдаёт верные предопределённые url"""
        test_array = YatubeURL_Path_Tests_reverse.templts_pgs_names_simple
        for page_url, dict_args in test_array.items():
            view_func, func_name = dict_args
            with self.subTest(page_url=page_url):
                # resp = self.test_class.guest_client.get(page_url)
                self.assertEqual(reverse(view_func), page_url)
                self.assertEqual(reverse(func_name), page_url)

    def test_reverse_url_args(self):
        """Проверка, что reverse() with args отдаёт верные url генерируемые"""
        test_array = YatubeURL_Path_Tests_reverse.templts_pgs_names_args
        for page_url, dict_args in test_array.items():
            view_func, func_name, args_array = dict_args
            with self.subTest(page_url=page_url):
                # resp = self.test_class.guest_client.get(page_url)
                self.assertEqual(reverse(view_func,
                                         kwargs=args_array), page_url)
                self.assertEqual(reverse(func_name,
                                         kwargs=args_array), page_url)


class YatubeURL_Path_isTemplates_right_Tests(TestCase):
    """Проверка правильности шаблонов по url-адресам

    URL                                     temlate
    '/'                                     posts/index.html
    '/group/'                               posts/group_index.html
    '/group/<slug:slug>/'                   posts/group.html
    '/new/'                                 posts/new_post.html
    '<str:username>/'                       posts/profile.html
    '<str:username>/<int:post_id>/'         posts/post.html
    '<str:username>/<int:post_id>/edit/'    posts/new_post.html
    '/about/author/'                        about/author.html
    '/about/tech/'                          about/tech.html
    '/signup/'                              users/signup.html
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # два тестовых юзера, один - автор поста
        cls.user_with_post = User.objects.create(
            username='poster_user'
        )
        cls.user_no_post = User.objects.create(
            username='silent_user'
        )
        # тестовая группа
        cls.group_test = Group.objects.create(
            title='test_group_title',
            slug='test-slug'
        )

        # тестовый пост
        cls.test_post = Post.objects.create(
            author=cls.user_with_post,
            text='test_post_text'
        )
        cls.test_post.save()
        cls.group_test.save()

        # неавторизованный клиент
        cls.guest_client = Client()
        # авторизованный клиент с постом
        cls.authorized_client_a = Client()
        cls.authorized_client_a.force_login(cls.user_with_post)
        # авторизованный клиент без поста
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_no_post)

        # набор пар "returned reverse url": ("views_name", "name")
        cls.templts_pgs_names_simple = {
            '/': (index, 'index'),
            '/group/': (group_index, 'group_index'),
            '/new/': (new_post, 'new_post'),
        }

        # набор пар "url": "имя шаблона"
        cls.templts_url_temlate_name = {
            '/': 'posts/index.html',
            '/group/': 'posts/group_index.html',
            '/group/test-slug/': 'posts/group.html',
            '/new/': 'posts/new_post.html',
            '/poster_user/': 'posts/profile.html',
            '/poster_user/1/': 'posts/post.html',
            '/poster_user/1/edit/': 'posts/new_post.html',
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
            '/auth/signup/': 'users/signup.html',
        }

    def test_right_temlate_use_with_url(self):
        """Проверка, что по запросу url используется верный шаблон"""
        test_class = YatubeURL_Path_isTemplates_right_Tests
        test_array = test_class.templts_url_temlate_name
        for page_url, temlat_name in test_array.items():

            with self.subTest(page_url=page_url):
                resp = test_class.authorized_client_a.get(page_url)
                self.assertTemplateUsed(resp, temlat_name)
