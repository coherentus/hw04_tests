from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import response
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


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
    - третий набор тестов GET запросов прямых ссылок через reverse()
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
        self.authorized_client_a = Client()
        self.authorized_client_a.force_login(
            UrlAbsPathTests.user_with_post
        )

        self.authorized_client = Client()
        self.authorized_client.force_login(
            UrlAbsPathTests.user_no_post
        )

    def tearDown(self):
        self.authorized_client_a.delete
        self.authorized_client.delete

    def test_get_abs_urls_with_200(self):
        # набор для первой группы тестов
        # (абсолютный урл, клиент - гостевой или авторизованный)
        group_slug = UrlAbsPathTests.group_test.slug
        user_no_post = UrlAbsPathTests.user_no_post.username
        user_with_post = UrlAbsPathTests.user_with_post.username
        post_id = UrlAbsPathTests.test_post.id
        guest_client = Client()
        user_client = self.authorized_client

        list_pgs_client = (
            ('/', guest_client),
            ('/group/', guest_client),
            (f'/group/{group_slug}/', guest_client),
            (f'/{user_no_post}/', guest_client),
            (f'/{user_with_post}/{post_id}/', guest_client),
            ('/new/', user_client),
        )

        for abs_url_client in list_pgs_client:
            abs_url, client = abs_url_client
            with self.subTest(abs_url=abs_url):
                resp = client.get(abs_url)
                self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_get_abs_url_redirects(self):
        """Проверка редиректов по абсолютному пути для разных клиентов

        "/<str:username>/<int:post_id>/edit/"   guest -> /login
                                                user -> /username/post_id/
        "/new/"                                 guest -> /login
        """
        guest_client = Client()
        user_client = self.authorized_client
        user_with_post = UrlAbsPathTests.user_with_post.username
        post_id = UrlAbsPathTests.test_post.id

        # набор для второй группы тестов
        # (url, client, client_type, redirected url [from reverse()])
        login_url = settings.LOGIN_URL

        path_new = '/new/'
        next_path_new = ''.join(['?next=', path_new])

        path_user_post_edit = f'/{user_with_post}/{post_id}/edit/'
        next_path_user_post_edit = ''.join(['?next=', path_user_post_edit])

        reverse_post = reverse('post', args=(user_with_post, post_id))

        list_pgs_client_redirect = (
            (path_new,
             guest_client, 'guest',
             ''.join([login_url, next_path_new])),

            (path_user_post_edit,
             guest_client, 'guest',
             ''.join([login_url, next_path_user_post_edit])),

            (path_user_post_edit,
             user_client, 'user',
             reverse_post),
        )

        for abs_url_client_redirect in list_pgs_client_redirect:
            abs_url, client, client_type, redirect = abs_url_client_redirect
            param = ''.join([abs_url, ' | ', client_type])
            with self.subTest(param=param):
                resp = client.get(abs_url)
                self.assertRedirects(resp, redirect)

    def test_url_name_reverse(self):
        """Проверка правильности url через reverse(name)
        
        name                url
        'index'             '/'
        'group_index'       'group/'
        'group'             'group/<slug:slug>/'
        'new_post'          'new/'
        'profile'           '<str:username>/'
        'post'              '<str:username>/<int:post_id>/'
        'post_edit'         '<str:username>/<int:post_id>/edit/'
        """
        username = UrlAbsPathTests.user_with_post.username
        post_id = UrlAbsPathTests.test_post.id
        slug = UrlAbsPathTests.group_test.slug

        # набор для третьей группы тестов
        # (name, url, args)
        list_name_url_args = (
            ('index', '/', None),
            ('group_index', '/group/', None),
            ('group', f'/group/{slug}/', (slug,)),
            ('new_post', '/new/', None),
            ('profile', f'/{username}/', (username,)),
            ('post', f'/{username}/{post_id}/', (username, post_id)),
            ('post_edit', f'/{username}/{post_id}/edit/', (username, post_id)),
        )

        for params in list_name_url_args:
            name, url, args = params
            msg = ''.join([name, ' | ', url])
            with self.subTest(msg=msg):
                self.assertEqual(url, reverse(name, args=args))
