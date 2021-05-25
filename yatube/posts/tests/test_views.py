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
    'index'             page: QuerySet[Post]
    'group'             page: QuerySet[Post], group: Grop
    'profile'           page: QuerySet[Post], profile_user: User
    'group_index'       page: QuerySet[Group]
    'post'              post: Post, author: Post.author
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

    def setUp(self):
        pass

    def page_queryset_post_test(self, queryset, client, view_name):
        guest_client = Client()
        db_post = ViewsContextTests.test_post
        response = client.get(reverse(view_name))
        # контекст содержит page
        self.assertIn('page', response.context)

        page_list = response.context.get(queryset).object_list
        first_object_post = page_list[0]
        self.assertIn(first_object_post, 'text')
        self.assertIn(first_object_post, 'author')
        self.assertIn(first_object_post, 'pub_date')

        post_text = first_object_post.text
        post_author = first_object_post.author
        post_pub_date = first_object_post.pub_date
        
        self.assertEqual(post_text, db_post.text)
        self.assertEqual(post_author, db_post.author)
        self.assertEqual(post_pub_date, db_post.pub_date)

    # страницы без форм, неавторизованный клиент
    # name "index"
    def test_index_put_in_render_right_context(self):
        """Проверка, что "index" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон page: QuerySet[Post]
        """
        guest_client = Client()
        self.page_queryset_post_test('page', guest_client, 'index')

        """response = guest_client.get(reverse('index'))
        # контекст содержит page
        self.assertFalse(response.context['page'] is None)

        # page содержит post, post содержит "text" "username" "pub_date"
        page_list = response.context.get('page').object_list
        first_object_post = page_list[0]
        post_text = first_object_post.text
        post_author = first_object_post.author
        post_pub_date = first_object_post.pub_date
        self.assertFalse(post_text is None)
        self.assertEqual(post_text, ViewsContextTests.test_post.text)
        self.assertFalse(post_author is None)
        self.assertEqual(post_author, ViewsContextTests.test_post.author)
        self.assertFalse(post_pub_date is None)
        self.assertEqual(post_pub_date, ViewsContextTests.test_post.pub_date)"""

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

        # контекст содержит page
        self.assertFalse(response.context['page'] is None)

        # page содержит post, post содержит "text" "username" "pub_date"
        page_list = response.context.get('page').object_list
        first_object_post = page_list[0]
        post_text = first_object_post.text
        post_author = first_object_post.author
        post_pub_date = first_object_post.pub_date
        self.assertFalse(post_text is None)
        self.assertEqual(post_text, ViewsContextTests.test_post.text)
        self.assertFalse(post_author is None)
        self.assertEqual(post_author, ViewsContextTests.test_post.author)
        self.assertFalse(post_pub_date is None)
        self.assertEqual(post_pub_date, ViewsContextTests.test_post.pub_date)

        # контекст содержит group
        self.assertFalse(response.context['group'] is None)
        object_group = response.context['group']
        group_description = object_group.description
        group_title = object_group.title
        group_slug = object_group.slug

        # есть ли group.description, равен ли тестовому полю
        self.assertFalse(group_description is None)
        self.assertEqual(group_description,
                         ViewsContextTests.group_test.description)
        # есть ли group.title, равен ли тестовому полю
        self.assertFalse(group_title is None)
        self.assertEqual(group_title, ViewsContextTests.group_test.title)

        # есть ли group.slug, равен ли тестовому полю
        self.assertFalse(group_slug is None)
        self.assertEqual(group_title, ViewsContextTests.group_test.title)

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

        # контекст содержит profile_user
        self.assertFalse(response.context['profile_user'] is None)
        object_user = response.context['profile_user']
        user_username = object_user.username

        # есть ли user.username, равен ли тестовому полю
        self.assertFalse(user_username is None)
        self.assertEqual(user_username, ViewsContextTests.user_test.username)

        # контекст содержит page
        self.assertFalse(response.context['page'] is None)

        # page содержит post, post содержит "text" "username" "pub_date"
        first_object_post = response.context['page'][0]
        post_text = first_object_post.text
        post_author = first_object_post.author
        post_pub_date = first_object_post.pub_date
        self.assertFalse(post_text is None)
        self.assertEqual(post_text, ViewsContextTests.test_post.text)
        self.assertFalse(post_author is None)
        self.assertEqual(post_author, ViewsContextTests.test_post.author)
        self.assertFalse(post_pub_date is None)
        self.assertEqual(post_pub_date, ViewsContextTests.test_post.pub_date)

    # name "group_index"
    def test_group_index_put_in_render_right_context(self):
        """Проверка, что "group_index" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон page: QuerySet[Group]
        """
        guest_client = Client()
        response = guest_client.get(reverse('group_index'))

        # контекст содержит page
        self.assertFalse(
            response.context['page'] is None)

        # page содержит group[], group содержит "title" "description" "slug"
        first_object_group = response.context['page'][0]
        group_title = first_object_group.title
        group_description = first_object_group.description
        group_slug = first_object_group.slug

        # group title
        self.assertFalse(group_title is None)
        self.assertEqual(group_title, ViewsContextTests.group_test.title)
        # group description
        self.assertFalse(group_description is None)
        self.assertEqual(group_description, ViewsContextTests.group_test.description)
        # group slug
        self.assertFalse(group_slug is None)
        self.assertEqual(group_slug, ViewsContextTests.group_test.slug)

    # name post
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
        self.assertFalse(response.context['post'] is None)
        self.assertFalse(response.context['author'] is None)
        # "post" равен тестовому посту
        self.assertEqual(response.context['post'], ViewsContextTests.test_post)
        # "author" из контекста равен тестовому юзеру
        self.assertEqual(response.context['author'], ViewsContextTests.user_test)


class YaTb_test_post_route_right_group(TestCase):
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

        # неавторизованный клиент
        cls.guest_client = Client()

    def setUp(self):
        self.test_class = YaTb_test_post_route_right_group

        # тестовый пост
        self.test_post = Post.objects.create(
            author=self.test_class.user_test,
            text='test_post_text',
            group=self.test_class.group_test_post
        )

    def test_post_after_create_in_index(self):
        """Проверка, что пост попадает на главную"""
        response = self.test_class.guest_client.get(reverse('index'))

        # post.id с главной и post.id созданного тестового поста
        self.assertEqual(
            response.context['page'][0].id,
            self.test_post.id
        )

    def test_post_after_create_in_self_group(self):
        """Проверка, что пост попадает в свою группу"""
        response = self.test_class.guest_client.get(
            reverse(
                'group',
                kwargs={'slug': self.test_class.group_test_post.slug}
            )
        )

        # post.id со страницы руппы и post.id созданного тестового поста
        self.assertEqual(
            response.context['page'][0].id, self.test_post.id)

    def test_post_after_create_not_in_another_group(self):
        """Проверка, что пост не попадает в чужую группу"""

        # новый пост для второй группы, чтобы "page" содержал объект
        self.test_class.test_post_2 = Post.objects.create(
            author=self.test_class.user_test,
            text='test_post_text',
            group=self.test_class.group_test_nopost
        )

        response = self.test_class.guest_client.get(
            reverse(
                'group',
                kwargs={'slug': self.test_class.group_test_nopost.slug}
            )
        )

        # post.id со страницы группы и post.id созданного тестового поста
        self.assertNotEqual(
            response.context['page'][0].id, self.test_post.id)


class YaTb_test_paginator_index_group_profile_groupindex(TestCase):
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
        for i in range(8):
            Group.objects.create(
                title='test_group_title_with_post' + str(i),
                description='test_description_for_test_group_of_post' + str(i),
                slug='test-slug-for-post' + str(i)
            )

        # тестовые посты для 'index' 'group' 'profile'
        for i in range(6):
            Post.objects.create(
                text='test_text_' + str(i),
                author=cls.user_test,
                group=Group.objects.get(id=1)
            )

        # неавторизованный клиент
        cls.guest_client = Client()

    def setUp(self):
        self.test_class = YaTb_test_paginator_index_group_profile_groupindex

        # набор для subTest 'index' 'group' 'profile'
        self.test_name_args = {
            'index': '',
            'group': {'slug': Group.objects.get(id=1).slug},
            'profile': {'username': self.test_class.user_test.username}
        }

    def test_item_posts_per_page(self):
        """Проверка, что все посты правильно разбиваются на страницы.

        Всего постов - 6,
        константа пагинатора - 4,
        Ожидаемая разбивка - 4 для первой страницы и 2 для второй(последней).
        """
        settings.PAGINATOR_DEFAULT_SIZE = 4
        test_array = self.test_name_args
        for name, args in test_array.items():

            with self.subTest(name=name):

                # Первая порция(страница)
                response = self.test_class.guest_client.get(
                    reverse(name, kwargs=args)
                )

                obj_list = response.context['page']
                self.assertEqual(
                    len(obj_list), settings.PAGINATOR_DEFAULT_SIZE,
                    ('Количество постов на первой странице "', name,
                     '" не равно константе settings.PAGINATOR_DEFAULT_SIZE.')
                )

                # Последняя порция(страница)
                response = self.test_class.guest_client.get(
                    reverse(name, kwargs=args) + '?page=2'
                )

                obj_list = response.context['page']
                self.assertEqual(
                    len(obj_list),
                    Post.objects.count() - settings.PAGINATOR_DEFAULT_SIZE,
                    ('Количество постов на второй странице "', name,
                     '" не равно остатку постов.')
                )

    def test_item_groups_per_page(self):
        """Проверка, что все группы правильно разбиваются на страницы.

        Всего групп - 8,
        константа пагинатора - 5,
        Ожидаемая разбивка - 5 для первой страницы и 3 для второй(последней).
        """
        settings.PAGINATOR_DEFAULT_SIZE = 5
        # Первая порция(страница)
        response = self.test_class.guest_client.get(
            reverse('group_index')
        )

        obj_list = response.context['page']
        self.assertEqual(
            len(obj_list), settings.PAGINATOR_DEFAULT_SIZE,
            ('Количество групп на первой странице "/group" не равно'
             ' константе settings.PAGINATOR_DEFAULT_SIZE.')
        )

        # Последняя порция(страница)
        response = self.test_class.guest_client.get(
            reverse('group_index') + '?page=2'
        )

        obj_list = response.context['page']
        self.assertEqual(
            len(obj_list),
            Group.objects.count() - settings.PAGINATOR_DEFAULT_SIZE,
            ('Количество групп на второй странице "/group" не равно'
             ' остатку постов.')
        )

