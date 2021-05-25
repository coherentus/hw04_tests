from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class URLPathTemplatesTests(TestCase):
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
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_with_post = User.objects.create(
            username='poster_user'
        )
        cls.user_no_post = User.objects.create(
            username='silent_user'
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
        # авторизованный клиент с постом
        self.authorized_client_a = Client()
        self.authorized_client_a.force_login(
            URLPathTemplatesTests.user_with_post
        )

    def test_right_temlate_use_with_url(self):
        """Проверка, что по запросу url используется верный шаблон"""
        group = URLPathTemplatesTests.group_test
        user_a = URLPathTemplatesTests.user_with_post
        post = URLPathTemplatesTests.test_post
        # набор пар ("url", "имя шаблона")
        array_url_temlate_name = (
            ('/', 'posts/index.html'),
            ('/group/', 'posts/group_index.html'),
            (f'/group/{group.slug}/', 'posts/group.html'),
            ('/new/', 'posts/new_post.html'),
            (f'/{user_a.username}/', 'posts/profile.html'),
            (f'/{user_a.username}/{post.id}/', 'posts/post.html'),
            (f'/{user_a.username}/{post.id}/edit/', 'posts/new_post.html'),
            ('/about/author/', 'about/author.html'),
            ('/about/tech/', 'about/tech.html')
        )

        for element in array_url_temlate_name:
            page_url, temlat_name = element
            param = ' | '.join([page_url, temlat_name])
            with self.subTest(param=param):
                resp = self.authorized_client_a.get(page_url)
                self.assertTemplateUsed(resp, temlat_name)


class ViewsContextTests(TestCase):
    """Проверка контекста, передаваемого из view в шаблоны

    name of view            верный контекст содержит
    'index'             page: QuerySet[Post], image: post.image
    'group'             page: QuerySet[Post], group: Grop, image: post.image
    'profile'           page: QuerySet[Post], profile_user: User, image: post.image
    'group_index'       page: QuerySet[Group]
    'post'              post: Post, author: Post.author, image: post.image
    'new_post'          form: PostForm, edit_flag: bool
    'post_edit'         form: PostForm, edit_flag: bool
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # тестовый юзер
        cls.user_test = User.objects.create(
            username='very_test_user'
        )

        # тестовая группа
        cls.group_test = Group.objects.create(
            title='test_group_title',
            description='test_description_for_test_group',
            slug='test-slug'
        )

        # тестовый пост
        cls.test_post = Post.objects.create(
            author=cls.user_test,
            text='test_post_text',
            group=cls.group_test
        )

    def page_queryset_post_test(self, response):
        post_in_db = ViewsContextTests.test_post
        # контекст содержит page
        self.assertIn('page', response.context)

        page_list = response.context.get('page').object_list
        post_in_context_page = page_list[0]
        self.assertEqual(post_in_context_page, post_in_db)

    # страницы без форм, неавторизованный клиент
    # name "index"
    def test_index_put_in_render_right_context(self):
        """Проверка, что "index" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон page: QuerySet[Post]
        """
        guest_client = Client()
        response = guest_client.get(reverse('index'))
        self.page_queryset_post_test(response)

    # name "group"
    def test_group_put_in_render_right_context(self):
        """Проверка, что "group" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон group: Group, page: QuerySet[Post]
        """
        guest_client = Client()
        response = guest_client.get(
            reverse(
                'group',
                kwargs={'slug': ViewsContextTests.group_test.slug}
            )
        )
        self.page_queryset_post_test(response)

        # контекст содержит group
        group_in_db = ViewsContextTests.group_test
        self.assertIn('group', response.context)
        group_in_context = response.context['group']
        self.assertEqual(group_in_context, group_in_db)

    # name "profile"
    def test_profile_put_in_render_right_context(self):
        """Проверка, что "profile" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон profile_user: User, page: QuerySet[Post]
        """
        guest_client = Client()
        response = guest_client.get(
            reverse(
                'profile',
                kwargs={'username': ViewsContextTests.user_test.username}
            )
        )
        self.page_queryset_post_test(response)

        # контекст содержит profile_user
        user_in_db = ViewsContextTests.user_test
        self.assertIn('profile_user', response.context)
        user_in_context = response.context['profile_user']
        self.assertEqual(user_in_context, user_in_db)

    # name "group_index"
    def test_group_index_put_in_render_right_context(self):
        """Проверка, что "group_index" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон page: QuerySet[Group]
        """
        guest_client = Client()
        response = guest_client.get(reverse('group_index'))

        # контекст содержит page
        self.assertIn('page', response.context)

        # page содержит group[], group содержит "title" "description" "slug"
        group_in_db = ViewsContextTests.group_test
        group_in_context = response.context['page'][0]
        self.assertEqual(group_in_context, group_in_db)

    # name "post"
    def test_post_put_in_render_right_context(self):
        """Проверка, что "post" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон post: Post, author: Post.author
        """
        guest_client = Client()
        response = guest_client.get(
            reverse(
                'post',
                kwargs={
                    'username': ViewsContextTests.user_test.username,
                    'post_id': ViewsContextTests.test_post.id
                }
            )
        )
        # контекст содержит post author
        self.assertIn('post', response.context)
        self.assertIn('author', response.context)
        post_in_db = ViewsContextTests.test_post
        post_in_context = response.context['post']
        user_in_db = ViewsContextTests.user_test
        user_in_context = response.context['author']
        # "post" равен тестовому посту
        self.assertEqual(post_in_context, post_in_db)
        # "author" из контекста равен тестовому юзеру
        self.assertEqual(user_in_context, user_in_db)

    def test_image_in_context(self):
        """Проверка присутствия в контексте страницы картинки поста.
        
        Присутствие картинки поста ожидается:
        name of view            верный контекст содержит
        'index'             image: post.image
        'group'             image: post.image
        'profile'           image: post.image
        'post'              image: post.image
        """
        guest_client = Client()
        group = ViewsContextTests.group_test
        user_a = ViewsContextTests.user_test
        post = ViewsContextTests.test_post
        test_array_urls = (
            ('/'),
            (f'/group/{group.slug}/'),
            (f'/{user_a.username}/'),
        )
        for url in test_array_urls:
            with self.subTest(url=url):
                response = guest_client.get(url)
                self.assertIn('page', response.context)
                page_list = response.context.get('page').object_list
                post_in_context_page = page_list[0]
                self.assertTrue(hasattr(post_in_context_page, 'image'))

        response = guest_client.get(f'/{user_a.username}/{post.id}/')
        post_in_context_page = response.context.get('post')
        self.assertTrue(hasattr(post_in_context_page, 'image'))


class PostRouteRightGroup(TestCase):
    """Проверка создания поста в группе

    После создания поста в группе, он должен:
    - появиться на главной странице
    - появиться на странице своей группы
    - отсутствовать на странице не своей группы
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # тестовый юзер автор поста
        cls.user_test = User.objects.create(
            username='very_test_user'
        )
        # тестовая группа для поста
        cls.group_test_post = Group.objects.create(
            title='test_group_title_with_post',
            description='test_description_for_test_group_of_post',
            slug='test-slug-for-post'
        )
        # тестовая группа для отсутствия поста
        cls.group_test_nopost = Group.objects.create(
            title='test_group_title_without_post',
            description='description_of_test_group_without_post',
            slug='test-slug-no-post'
        )

    def setUp(self):
        # тестовый пост
        PostRouteRightGroup.test_post = Post.objects.create(
            author=PostRouteRightGroup.user_test,
            text='test_post_text',
            group=PostRouteRightGroup.group_test_post
        )

    def test_post_after_create_in_index(self):
        """Проверка, что пост попадает на главную"""
        guest_client = Client()
        response = guest_client.get(reverse('index'))

        # post с главной и post созданный
        self.assertEqual(
            response.context['page'][0],
            PostRouteRightGroup.test_post
        )

    def test_post_after_create_in_self_group(self):
        """Проверка, что пост попадает в свою группу"""
        guest_client = Client()
        response = guest_client.get(
            reverse(
                'group',
                kwargs={'slug': PostRouteRightGroup.group_test_post.slug}
            )
        )

        # post со страницы руппы и post созданный тестовоый пост
        self.assertEqual(
            response.context['page'][0], PostRouteRightGroup.test_post)

    def test_post_after_create_not_in_another_group(self):
        """Проверка, что пост не попадает в чужую группу"""

        # новый пост для второй группы, чтобы "page" содержал объект
        PostRouteRightGroup.test_post_2 = Post.objects.create(
            author=PostRouteRightGroup.user_test,
            text='test_post_text',
            group=PostRouteRightGroup.group_test_nopost
        )

        guest_client = Client()
        response = guest_client.get(
            reverse(
                'group',
                kwargs={'slug': PostRouteRightGroup.group_test_nopost.slug}
            )
        )

        # post со страницы группы и post созданный тестовоый пост
        self.assertNotEqual(
            response.context['page'][0], PostRouteRightGroup.test_post)


class PaginatorWorkRight(TestCase):
    """Проверка пагинатора для всех страниц, где он должен работать

    view_name           objects
    'index'             posts
    'group'             posts
    'profile'           posts
    'group_index'       groups
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # тестовый юзер автор постов
        cls.user_test = User.objects.create(
            username='very_test_user'
        )

        # тестовые группы для 'group_index'
        groups_12 = (
            Group(title='Test %s' % i,
                  description='test_description%s' % i,
                  slug='test-slug-%s' % i) for i in range(12)
        )
        Group.objects.bulk_create(groups_12)

        # тестовые посты для 'index' 'group' 'profile'
        posts_12 = (
            Post(text='test_text_%s' % i,
                 author=cls.user_test,
                 group=Group.objects.get(id=1)) for i in range(12)
        )
        Post.objects.bulk_create(posts_12)

    def setUp(self):
        # набор для subTest 'index' 'group' 'profile'
        self.test_name_args = {
            'index': '',
            'group': {'slug': Group.objects.get(id=1).slug},
            'profile': {'username': PaginatorWorkRight.user_test.username}
        }

    def test_item_posts_per_page(self):
        """Проверка, что все посты правильно разбиваются на страницы.

        Всего постов - 12,
        константа пагинатора - 10,
        Ожидаемая разбивка - 10 для первой страницы и 2 для второй(последней).
        """
        guest_client = Client()
        test_array = self.test_name_args
        for name, args in test_array.items():

            with self.subTest(name=name):

                # Первая порция(страница)
                response = guest_client.get(
                    reverse(name, kwargs=args)
                )

                obj_list = response.context['page']
                self.assertEqual(
                    len(obj_list), settings.PAGINATOR_DEFAULT_SIZE
                )

                # Последняя порция(страница)
                response = guest_client.get(
                    reverse(name, kwargs=args) + '?page=2'
                )

                obj_list = response.context['page']
                self.assertEqual(
                    len(obj_list),
                    Post.objects.count() - settings.PAGINATOR_DEFAULT_SIZE
                )

    def test_item_groups_per_page(self):
        """Проверка, что все группы правильно разбиваются на страницы.

        Всего групп - 12,
        константа пагинатора - 10,
        Ожидаемая разбивка - 10 для первой страницы и 2 для второй(последней).
        """
        guest_client = Client()
        # Первая порция(страница)
        response = guest_client.get(
            reverse('group_index')
        )

        obj_list = response.context['page']
        self.assertEqual(
            len(obj_list), settings.PAGINATOR_DEFAULT_SIZE
        )

        # Последняя порция(страница)
        response = guest_client.get(
            reverse('group_index') + '?page=2'
        )

        obj_list = response.context['page']
        self.assertEqual(
            len(obj_list),
            Group.objects.count() - settings.PAGINATOR_DEFAULT_SIZE
        )
