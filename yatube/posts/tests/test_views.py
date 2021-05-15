from random import randint

from django import forms
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
            text='test_post_text'
        )
        cls.test_post.save()
        cls.group_test.save()

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
        response = self.test_class.guest_client.get(reverse('group_index'))






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

На главной странице, странице группы и на странице профайла пользователя проверьте паджинатор: убедитесь, что в словарь context передаётся по 10 записей на страницу.


"""
