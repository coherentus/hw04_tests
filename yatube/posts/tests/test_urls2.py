from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.views import (index, group_index, new_post, profile, post_edit,
                         post_view, group_posts)

User = get_user_model()


class SmokeURLTests(TestCase):

    def test_smoke(self):
        """'Дымовой тест. Проверка, что на запрос '/' ответ 200."""
        guest_client = Client()
        static_url = ('/')
        response = guest_client.get(static_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class UrlAbsPathTests(TestCase):
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
    Методика тестов:
    - первый набор тестов GET запросов по абсолютному пути без редиректов.
    Клиенты гостевой и авторизованный[автор/не автор]
    - второй набор тестов всех возможных редиректов GET запросов.
    Клиенты гостевой и авторизованный
    - третий набор тестов GET запросов прямых ссылок и reverse()
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_with_post = User.objects.create(
            username='poster'
        )
        cls.user_no_post = User.objects.create(
            username='silent'
        )

        cls.group_test = Group.objects.create(
            title='test_group_title',
            slug='test-slug'
        )

        cls.test_post = Post.objects.create(
            author=cls.user_with_post,
            text='test_post_text'
        )

    def setUp(self):
        self.guest_client = Client()
        UrlAbsPathTests.authorized_client_a = Client()
        UrlAbsPathTests.authorized_client_a.force_login(
            UrlAbsPathTests.user_with_post
        )

        UrlAbsPathTests.authorized_client = Client()
        UrlAbsPathTests.authorized_client.force_login(
            UrlAbsPathTests.user_no_post
        )

    def test_get_abs_urls_with_200(self):
        # набор для первой группы тестов
        # (абсолютный урл, клиент - гостевой или авторизованный)
        group_slug = UrlAbsPathTests.group_test.slug
        user_no_post = UrlAbsPathTests.user_no_post.username
        user_with_post = UrlAbsPathTests.user_with_post.username
        post_id = UrlAbsPathTests.test_post.id
        guest_client = Client()
        user_client = UrlAbsPathTests.authorized_client
        author_client = UrlAbsPathTests.authorized_client_a

        list_pgs_client = (
            ('/', guest_client),
            ('/group/', guest_client),
            (f'/group/{group_slug}/', guest_client),
            (f'/{user_no_post}/', guest_client),
            (f'/{user_with_post}/{post_id}/', guest_client),
            (f'/{user_with_post}/{post_id}/edit', author_client),
            ('/new', user_client),
        )

        for abs_url_client in list_pgs_client:
            abs_url, client = abs_url_client
            with self.subTest(abs_url=abs_url):
                resp = client.get(abs_url)
                self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_get_abs_url_redirects(self):
        """Проверка редиректов по абсолютному пути для разных клиентов

        "/<str:username>/<int:post_id>/edit/"   g->/login
                                                u->/username/post_id/
        "/new/"                                 g->/login
        """
        guest_client = Client()
        user_client = UrlAbsPathTests.authorized_client
        user_with_post = UrlAbsPathTests.user_with_post.username
        post_id = UrlAbsPathTests.test_post.id

        # набор для второй группы тестов
        # (url, client, redirected url from reverse())
        list_pgs_client_redirect = (
            ('/new/', guest_client, '/auth/login/'),

            (f'/{user_with_post}/{post_id}/edit',
             guest_client, '/auth/login/'),

            (f'/{user_with_post}/{post_id}/edit',
             user_client,
             reverse('post', args=(user_with_post, post_id))),
        )

        for abs_url_client_redirect in list_pgs_client_redirect:
                abs_url, client, redirect = abs_url_client_redirect
                with self.subTest(abs_url=abs_url):
                    resp = client.get(abs_url)
                    self.assertRedirects(resp, redirect)




    def test_guest_get_nonautorized_pages(self):
        """Проверка, что guest видит доступные страницы"""
        for page_url, resp_code in UrlAbsPathTests.templts_pgs_names.items():

            with self.subTest(page_url=page_url):
                resp = UrlAbsPathTests.guest_client.get(page_url)
                self.assertEqual(resp.status_code, resp_code, page_url)

    # проверка редиректов по абсолютным путям
    # guest "new/" -> "login/"
    # method == GET
    def test_guest_abs_new_redirect_login_get(self):
        """Проверка, что guest GET /new -> /auth/login/?next=/new/"""
        resp = self.guest_client.get('/new/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/auth/login/?next=/new/')

    # method == POST
    def test_guest_abs_new_redirect_login_post(self):
        """Проверка, что guest POST /new -> /auth/login/?next=/new/"""
        resp = self.guest_client.post('/new/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/auth/login/?next=/new/')

    # guest GET "<username>/post_id/edit" -> "login/"
    def test_guest_abs_edit_redirect_login_get(self):
        """Проверка, что guest GET /user/post/edit -> /auth/login/?next=..."""
        resp = self.guest_client.get('/poster/1/edit/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/auth/login/?next=/poster/1/edit/')

    # guest POST "<username>/post_id/edit" -> "login/"
    def test_guest_abs_edit_redirect_login_post(self):
        """Проверка, что guest POST /user/post/edit -> /auth/login/?next=..."""
        resp = self.guest_client.post('/poster/1/edit/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/auth/login/?next=/poster/1/edit/')

    # user-not-author "<username>/post_id/edit" -> "<username>/post_id/"
    # method == GET
    def test_user_abs_edit_redirect_postcard_get(self):
        """Проверка, что не автор GET /user/post/edit -> /user/post/"""
        resp = self.authorized_client.get('/poster/1/edit/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/poster/1/')

    # method == POST
    def test_user_abs_edit_redirect_postcard_post(self):
        """Проверка, что не автор POST /user/post/edit -> /user/post/"""
        resp = UrlAbsPathTests.authorized_client.post('/poster/1/edit/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/poster/1/')

    # user-author "<username>/post_id/edit" 200
    # method == GET
    def test_user_author_abs_edit_redirect_postcard_get(self):
        """Проверка, что автор GET /user/post/edit == status 200"""
        resp = UrlAbsPathTests.authorized_client_a.get('/poster/1/edit/')
        self.assertEqual(resp.status_code, 200)

    # method == POST
    def test_user_author_abs_edit_redirect_postcard_post(self):
        """Проверка, что автор POST /user/post/edit == status 200"""
        resp = UrlAbsPathTests.authorized_client_a.post('/poster/1/edit/')
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



