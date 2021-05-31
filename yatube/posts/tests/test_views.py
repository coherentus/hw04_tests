from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.forms import PostForm

User = get_user_model()


class URLPathTemplatesTests(TestCase):
    """Проверка правильности шаблонов по url-адресам.

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
        self.authorized_author = Client()
        self.authorized_author.force_login(
            URLPathTemplatesTests.user_with_post
        )

    def test_right_temlate_use_with_url(self):
        """Проверка, что по запросу url используется верный шаблон."""
        group = URLPathTemplatesTests.group_test
        user_author = URLPathTemplatesTests.user_with_post
        post = URLPathTemplatesTests.test_post

        url_template_name = (
            ('index', None, 'index.html'),
            ('group_index', None, 'group_index.html'),
            ('group', (group.slug,), 'group.html'),
            ('new_post', None, 'new_post.html'),
            ('profile', (user_author.username,), 'profile.html'),
            ('post', (user_author.username, post.id), 'post.html'),
            ('post_edit', (user_author.username, post.id), 'new_post.html'),
        )

        for func_name, args, template_name in url_template_name:
            with self.subTest(url=reverse(func_name, args=args),
                              template=template_name):
                resp = self.authorized_author.get(
                    reverse(func_name, args=args)
                )
                self.assertTemplateUsed(resp, f'posts/{template_name}')


class ViewsContextTests(TestCase):
    """Проверка контекста, передаваемого из view в шаблоны.

    name of view            верный контекст содержит
    'index'             page: QuerySet[Post]
    'group'             page: QuerySet[Post], group: Group
    'profile'           page: QuerySet[Post], profile_user: User
    'group_index'       page: QuerySet[Group]
    'post'              post: Post, author: Post.author
    'new_post'          form: PostForm, edit_flag: bool
    'post_edit'         form: PostForm, edit_flag: bool
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_test = User.objects.create(
            username='very_test_user'
        )
        cls.group_test = Group.objects.create(
            title='test_group_title',
            description='test_description_for_test_group',
            slug='test-slug'
        )
        cls.test_post = Post.objects.create(
            author=cls.user_test,
            text='test_post_text',
            group=cls.group_test
        )

    def page_queryset_post_test(self, context, find_object):
        post_in_db = ViewsContextTests.test_post
        self.assertIn(find_object, context)
        if find_object == 'page':
            page_list = context.get(find_object).object_list
            post_in_context = page_list[0]
        elif find_object == 'post':
            post_in_context = context['post']

        self.assertEqual(post_in_context, post_in_db)
        self.assertEqual(post_in_context.text, post_in_db.text)
        self.assertEqual(post_in_context.author, post_in_db.author)
        self.assertEqual(post_in_context.group, post_in_db.group)
        self.assertEqual(post_in_context.pub_date, post_in_db.pub_date)

    def test_index_put_in_render_right_context(self):
        """Проверка, что "index" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон page: QuerySet[Post].
        """
        response = self.client.get(reverse('index'))
        self.page_queryset_post_test(response.context, 'page')

    def test_group_put_in_render_right_context(self):
        """Проверка, что "group" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон group: Group, page: QuerySet[Post].
        """
        response = self.client.get(
            reverse(
                'group', args=(ViewsContextTests.group_test.slug,)
            )
        )
        self.page_queryset_post_test(response.context, 'page')

        group_in_db = ViewsContextTests.group_test
        self.assertIn('group', response.context)
        group_in_context = response.context['group']
        self.assertEqual(group_in_context, group_in_db)
        self.assertEqual(group_in_context.title, group_in_db.title)
        self.assertEqual(group_in_context.description,
                         group_in_db.description)

    def test_profile_put_in_render_right_context(self):
        """Проверка, что "profile" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон profile_user: User, page: QuerySet[Post].
        """
        response = self.client.get(
            reverse(
                'profile',
                kwargs={'username': ViewsContextTests.user_test.username}
            )
        )
        self.page_queryset_post_test(response.context, 'page')

        user_in_db = ViewsContextTests.user_test
        self.assertIn('profile_user', response.context)
        user_in_context = response.context['profile_user']
        self.assertEqual(user_in_context, user_in_db)

    def test_group_index_put_in_render_right_context(self):
        """Проверка, что "group_index" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон page: QuerySet[Group].
        """
        response = self.client.get(reverse('group_index'))
        self.assertIn('page', response.context)

        group_in_db = ViewsContextTests.group_test
        group_in_context = response.context['page'][0]
        self.assertEqual(group_in_context, group_in_db)
        self.assertEqual(group_in_context.title, group_in_db.title)
        self.assertEqual(group_in_context.description,
                         group_in_db.description)
        self.assertEqual(group_in_context.slug, group_in_db.slug)

    def test_post_put_in_render_right_context(self):
        """Проверка, что "post" выдаёт верный контекст в шаблон.

        Должно передаваться в шаблон post: Post, author: Post.author
        """
        response = self.client.get(
            reverse(
                'post',
                args=(ViewsContextTests.user_test.username,
                      ViewsContextTests.test_post.id)
            )
        )
        self.page_queryset_post_test(response.context, 'post')

        self.assertIn('author', response.context)
        user_in_db = ViewsContextTests.user_test
        user_in_context = response.context['author']
        self.assertEqual(user_in_context, user_in_db)

    def test_new_post_put_in_render_right_context(self):
        """Проверка, что "new_post" выдаёт в шаблон верный контекст.

        В шаблон должны передаваться form: PostForm, edit_flag: bool.
        """
        authorize_writer = Client()
        authorize_writer.force_login(ViewsContextTests.user_test)
        response = authorize_writer.get(reverse('new_post'))
        self.assertIn('edit_flag', response.context)
        self.assertIs(response.context['edit_flag'], False)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit_put_in_render_right_context(self):
        """Проверка, что "post_edit" выдаёт в шаблон верный контекст.

        В шаблон должны передаваться form: PostForm, edit_flag: bool.
        """
        authorize_writer = Client()
        authorize_writer.force_login(ViewsContextTests.user_test)
        post_for_edit = ViewsContextTests.test_post

        response = authorize_writer.get(
            reverse(
                'post_edit',
                args=(post_for_edit.author, post_for_edit.id)
            )
        )
        self.assertIn('edit_flag', response.context)
        self.assertIs(response.context['edit_flag'], True)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)


class PostRouteRightGroup(TestCase):
    """Проверка создания поста в группе.

    После создания поста в группе, он должен:
    - появиться на главной странице
    - появиться на странице своей группы
    - отсутствовать на странице не своей группы
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(
            username='very_test_user'
        )
        cls.group_test_post = Group.objects.create(
            title='test_group_title_with_post',
            description='test_description_for_test_group_of_post',
            slug='test-slug-for-post'
        )
        cls.group_test_nopost = Group.objects.create(
            title='test_group_title_without_post',
            description='description_of_test_group_without_post',
            slug='test-slug-no-post'
        )

    def setUp(self):
        self.test_post = Post.objects.create(
            author=PostRouteRightGroup.user_author,
            text='test_post_text',
            group=PostRouteRightGroup.group_test_post
        )

    def test_post_after_create_in_index(self):
        """Проверка, что пост попадает на главную."""
        response = self.client.get(reverse('index'))

        self.assertEqual(
            response.context['page'][0],
            self.test_post
        )

    def test_post_after_create_in_self_group(self):
        """Проверка, что пост попадает в свою группу."""
        response = self.client.get(
            reverse(
                'group', args=(PostRouteRightGroup.group_test_post.slug,)
            )
        )
        self.assertEqual(response.context['page'][0], self.test_post)

    def test_post_after_create_not_in_another_group(self):
        """Проверка, что пост не попадает в чужую группу."""

        response = self.client.get(
            reverse(
                'group', args=(PostRouteRightGroup.group_test_nopost.slug,)
            )
        )
        self.assertEqual(len(response.context['page']), 0)


class PaginatorWorkRight(TestCase):
    """Проверка пагинатора для главной страницы.

    view_name           objects
    'index'             posts
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_test = User.objects.create(
            username='very_test_user'
        )

        test_group = Group.objects.create(
            title='Test group',
            description='test_description',
            slug='test-slug-s'
        )

        posts_12 = (
            Post(text='test_text_%s' % i,
                 author=cls.user_test,
                 group=test_group) for i in range(12)
        )
        Post.objects.bulk_create(posts_12)

    def test_item_posts_per_page(self):
        """Проверка, что все посты правильно разбиваются на страницы.

        12-ть постов должны распределиться на 2 страницы.
        """
        response = self.client.get(reverse('index'))

        obj_list = response.context['page']
        self.assertEqual(
            len(obj_list), settings.PAGINATOR_DEFAULT_SIZE
        )

        response = self.client.get(reverse('index') + '?page=2')

        obj_list = response.context['page']
        self.assertEqual(
            len(obj_list),
            Post.objects.count() - settings.PAGINATOR_DEFAULT_SIZE
        )
