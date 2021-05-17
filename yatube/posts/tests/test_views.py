from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class YaTb_test_views_context_without_form(TestCase):
    """Проверка контекста, передаваемого из view в шаблоны

    name of view            верный контекст содержит
    'index'             page: List[Post]
    'group'             group: Grop, page: List[Post]
    'profile'           profile_user: User, page: List[Post]
    'group_index'       page: List[Group]
    'post'              post: Post, author: Post.author
    'new_post'          form: PostForm, edit_flag: bool
    'post_edit'         form: PostForm, edit_flag: bool
    Проверка правильности вызова шаблонов определена в test_urls
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
            description = 'test_description_for_test_group',
            slug='test-slug'
        )

        # тестовый пост
        cls.test_post = Post.objects.create(
            author=cls.user_test,
            text='test_post_text',
            group=cls.group_test
        )

        # неавторизованный клиент
        cls.guest_client = Client()

    def setUp(self):
        self.test_class = YaTb_test_views_context_without_form

    # страницы без форм, неавторизованный клиент
    # name "index"   
    def test_index_put_in_render_right_context(self):
        """Проверка, что "index" выдаёт верный контекст в шаблон.
        
        Должно передаваться в шаблон page: List[Post]
        """
        response = self.test_class.guest_client.get(reverse('index'))
        # контекст содержит page
        self.assertFalse(response.context['page'] is None,
            'Из view "index" в шаблон не передаётся "page"'
        )
        # page содержит post, post содержит "text" "username" "pub_date"
        page_list = response.context.get('page').object_list
        first_object_post = page_list[0]
        post_text = first_object_post.text
        post_author = first_object_post.author
        post_pub_date = first_object_post.pub_date
        self.assertFalse(post_text is None, 
            'Первый объект "post" не содержит "text"'
        )
        self.assertEqual(post_text, self.test_class.test_post.text,
            '"text" из первого "post" не равен "text" тестового поста'
        )
        self.assertFalse(post_author is None,
            'Первый объект "post" не содержит "author"'
        )
        self.assertEqual(post_author, self.test_class.test_post.author,
            '"author" из первого "post" не равен "author" тестового поста'
        )
        self.assertFalse(post_pub_date is None,
            'Первый объект "post" не содержит "post_pub_date"'
        )
        self.assertEqual(post_pub_date, self.test_class.test_post.pub_date,
            '"pub_date" из первого "post" не равен "pub_date" тестового поста'
        )

    # name "group"
    def test_group_put_in_render_right_context(self):
        """Проверка, что "group" выдаёт верный контекст в шаблон.
        
        Должно передаваться в шаблон group: Group, page: List[Post]
        """
        response = self.test_class.guest_client.get(
            reverse('group',
            kwargs={'slug': self.test_class.group_test.slug})
        )
        
        # контекст содержит page
        self.assertFalse(response.context['page'] is None,
            'Из view "group" в шаблон не передаётся "page"'
        )
        # page содержит post, post содержит "text" "username" "pub_date"
        page_list = response.context.get('page').object_list
        first_object_post = page_list[0]
        post_text = first_object_post.text
        post_author = first_object_post.author
        post_pub_date = first_object_post.pub_date
        self.assertFalse(post_text is None, 
            'Первый объект "post" не содержит "text"'
        )
        self.assertEqual(post_text, self.test_class.test_post.text,
            '"text" из первого "post" не равен "text" тестового поста'
        )
        self.assertFalse(post_author is None,
            'Первый объект "post" не содержит "author"'
        )
        self.assertEqual(post_author, self.test_class.test_post.author,
            '"author" из первого "post" не равен "author" тестового поста'
        )
        self.assertFalse(post_pub_date is None,
            'Первый объект "post" не содержит "post_pub_date"'
        )
        self.assertEqual(post_pub_date, self.test_class.test_post.pub_date,
            '"pub_date" из первого "post" не равен "pub_date" тестового поста'
        )

        # контекст содержит group
        self.assertFalse(response.context['group'] is None,
            'Из view "group" в шаблон не передаётся "group"'
        )
        object_group = response.context['group']
        group_description = object_group.description
        group_title = object_group.title
        group_slug = object_group.slug
        
        # есть ли group.description, равен ли тестовому полю
        self.assertFalse(group_description is None,
            'Объект "group" не содержит "group.description"'
        )
        self.assertEqual(group_description,
            self.test_class.group_test.description,
            ('"group.description" из "group" не равен'
             ' "group.description" тестовой группы')
        )
        # есть ли group.title, равен ли тестовому полю
        self.assertFalse(group_title is None,
            'Объект "group" не содержит "title"'
        )
        self.assertEqual(group_title,
            self.test_class.group_test.title,
            ('"group.title" из первого "group" не равен'
             ' "group.title" тестовой группы')
        )

        # есть ли group.slug, равен ли тестовому полю
        self.assertFalse(group_slug is None,
            'Объект "group" не содержит "group.slug"'
        )
        self.assertEqual(group_title,
            self.test_class.group_test.title,
            ('"group.slug" из "group" не равен'
             ' "group.slug" тестовой группы')
        )

    # name "profile"
    def test_profile_put_in_render_right_context(self):
        """Проверка, что "profile" выдаёт верный контекст в шаблон.
        
        Должно передаваться в шаблон profile_user: User, page: List[Post]
        """
        response = self.test_class.guest_client.get(
            reverse('profile',
            kwargs={'username': self.test_class.user_test.username})
        )
        
        # контекст содержит profile_user
        self.assertFalse(response.context['profile_user'] is None,
            'Из view "profile" в шаблон не передаётся "profile_user"'
        )
        object_user = response.context['profile_user']
        user_username = object_user.username

        # есть ли user.username, равен ли тестовому полю
        self.assertFalse(user_username is None,
            'Объект "profile_user" не содержит "username"'
        )
        self.assertEqual(user_username,
            self.test_class.user_test.username,
            ('"username" из  "profile_user" не равен'
             ' "username" тестового юзера')
        )

        # контекст содержит page
        self.assertFalse(response.context['page'] is None,
            'Из view "profile" в шаблон не передаётся "page"'
        )
        # page содержит post, post содержит "text" "username" "pub_date"
        first_object_post = response.context['page'][0]
        post_text = first_object_post.text
        post_author = first_object_post.author
        post_pub_date = first_object_post.pub_date
        self.assertFalse(post_text is None, 
            'Первый объект "post" не содержит "text"'
        )
        self.assertEqual(post_text, self.test_class.test_post.text,
            '"text" из первого "post" не равен "text" тестового поста'
        )
        self.assertFalse(post_author is None,
            'Первый объект "post" не содержит "author"'
        )
        self.assertEqual(post_author, self.test_class.test_post.author,
            '"author" из первого "post" не равен "author" тестового поста'
        )
        self.assertFalse(post_pub_date is None,
            'Первый объект "post" не содержит "post_pub_date"'
        )
        self.assertEqual(post_pub_date, self.test_class.test_post.pub_date,
            '"pub_date" из первого "post" не равен "pub_date" тестового поста'
        )

    # name "group_index"
    def test_group_index_put_in_render_right_context(self):
        """Проверка, что "group_index" выдаёт верный контекст в шаблон.
        
        Должно передаваться в шаблон page: List[Group]
        """
        response = self.test_class.guest_client.get(reverse('group_index'))
        
        # контекст содержит page
        self.assertFalse(response.context['page'] is None,
            'Из view "group_index" в шаблон не передаётся "page"'
        )
        # page содержит group[], group содержит "title" "description" "slug"
        first_object_group = response.context['page'][0]
        group_title = first_object_group.title
        group_description = first_object_group.description
        group_slug = first_object_group.slug

        # group title
        self.assertFalse(group_title is None, 
            'Первый объект "group" не содержит "title"'
        )
        self.assertEqual(group_title, self.test_class.group_test.title,
            '"title" из первого "group" не равен "title" тестового поста'
        )
        # group description
        self.assertFalse(group_description is None,
            'Первый объект "group" не содержит "description"'
        )
        self.assertEqual(group_description, self.test_class.group_test.description,
            ('"description" из первого "group"'
            ' не равен "description" тестовой группы')
        )
        # group slug
        self.assertFalse(group_slug is None,
            'Первый объект "post" не содержит "slug"'
        )
        self.assertEqual(group_slug, self.test_class.group_test.slug,
            '"slug" из первого "group" не равен "slug" тестовой группы'
        )

    # name post
    def test_post_put_in_render_right_context(self):
        """Проверка, что "post" выдаёт верный контекст в шаблон.
        
        Должно передаваться в шаблон post: Post, author: Post.author
        """
        response = self.test_class.guest_client.get(
            reverse('post',
                kwargs={'username': self.test_class.user_test.username,
                        'post_id': self.test_class.test_post.id}
            )
        )
        # контекст содержит post author
        self.assertFalse(response.context['post'] is None,
            'Из view "post_view" в шаблон не передаётся "post"'
        )
        self.assertFalse(response.context['author'] is None,
            'Из view "post_view" в шаблон не передаётся "author"'
        )
        # "post" равен тестовому посту
        self.assertEqual(response.context['post'], self.test_class.test_post,
            '"post" из контекста не равен тестовому посту'
        )
        # "author" из контекста равен тестовому юзеру
        self.assertEqual(response.context['author'], self.test_class.user_test,
            '"author" из контекста не равен тестовому юзеру'
        )

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
            description = 'test_description_for_test_group_of_post',
            slug='test-slug-for-post'
        )
        # тестовая группа для отсутствия поста
        cls.group_test_nopost = Group.objects.create(
            title='test_group_title_without_post',
            description = 'description_of_test_group_without_post',
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
        self.assertEqual(response.context['page'][0].id,
            self.test_post.id,
            'Созданный пост не показался на главной'
        )

    def test_post_after_create_in_self_group(self):
        """Проверка, что пост попадает в свою группу"""
        response = self.test_class.guest_client.get(
            reverse('group',
                kwargs={'slug': self.test_class.group_test_post.slug}
            )
        )

        # post.id со страницы руппы и post.id созданного тестового поста
        self.assertEqual(response.context['page'][0].id,
            self.test_post.id,
            'Созданный пост не показался на странице группы'
        )

    def test_post_after_create_not_in_another_group(self):
        """Проверка, что пост не попадает в чужую группу"""
        
        # новый пост для второй группы, чтобы "page" содержал объект
        self.test_class.test_post_2 = Post.objects.create(
            author=self.test_class.user_test,
            text='test_post_text',
            group=self.test_class.group_test_nopost
        )

        response = self.test_class.guest_client.get(
            reverse('group',
                kwargs={'slug': self.test_class.group_test_nopost.slug}
            )
        )

        # post.id со страницы группы и post.id созданного тестового поста
        self.assertNotEqual(response.context['page'][0].id,
            self.test_post.id,
            'Созданный пост оказался на странице чужой группы'
        )


class YaTb_test_paginator_index_group_profile_groupindex(TestCase):
    """Проверка пагинатора для всех страниц, где он должен работать

    view_name           objects
    'index'             posts
    'group'             posts
    'profile'           posts
    'group_index'       groups
    для проверки переопределяется константа settings.PAGINATOR_DEFAULT_SIZE
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
                description = 'test_description_for_test_group_of_post' + str(i),
                slug='test-slug-for-post' + str(i)
        )
        
        # тестовые посты для 'index' 'group' 'profile'
        for i in range(6):
            Post.objects.create(
                text = 'test_text_'+str(i),
                author = cls.user_test,
                group = Group.objects.get(id=1)
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
                    reverse(name, kwargs = args)                
                )
                
                obj_list = response.context['page']
                self.assertEqual(len(obj_list),
                    settings.PAGINATOR_DEFAULT_SIZE,
                    ('Количество постов на первой странице "', name,
                    '" не равно константе settings.PAGINATOR_DEFAULT_SIZE.')
                )

                # Последняя порция(страница)
                response = self.test_class.guest_client.get(
                    reverse(name, kwargs=args) + '?page=2'                
                )
                
                obj_list = response.context['page']
                self.assertEqual(len(obj_list),
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
            self.assertEqual(len(obj_list),
                settings.PAGINATOR_DEFAULT_SIZE,
                ('Количество групп на первой странице "/group" не равно'
                ' константе settings.PAGINATOR_DEFAULT_SIZE.')
            )

            # Последняя порция(страница)
            response = self.test_class.guest_client.get(
                reverse('group_index') + '?page=2'                
            )
            
            obj_list = response.context['page']
            self.assertEqual(len(obj_list),
                Group.objects.count() - settings.PAGINATOR_DEFAULT_SIZE,
                ('Количество групп на второй странице "/group" не равно'
                ' остатку постов.')
            )



    






    

"""Проверка 
Проверьте, соответствует ли ожиданиям словарь context, передаваемый в шаблон при вызове
главной страницы,
страницы группы,
страницы создания поста,
страницы редактирования поста /<username>/<post_id>/edit/;
страницы профайла пользователя /<username>/,
страницы отдельного поста /<username>/<post_id>/,

Проверьте, что если при создании поста указать группу, то этот пост появляется
на главной странице сайта,
на странице выбранной группы.
Проверьте, что этот пост не попадает в группу, для которой не был предназначен.

На главной странице, странице группы и на странице профайла пользователя проверьте паджинатор:
 убедитесь, что в словарь context передаётся по 10 записей на страницу.


"""
