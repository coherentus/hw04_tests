import shutil
import tempfile
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class TestCreateEditPostForm(TestCase):
    """Проверка работы формы PostForm для создания поста."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(
            username='test_user_author',
        )

        cls.test_group = Group.objects.create(
            title='test_group_for_test_form',
            description='Description of test group',
            slug='slug_for_form'
        )
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        author = TestCreateEditPostForm.user_author
        self.authorized_author.force_login(author)

    def test_create_post_user(self):
        """Проверка, что после валидации добавляется пост.

        Методика проверки:
        - общее количество постов увеличилось на единицу.
        - поля созданного поста соответствуют полям формы.
        - после создания поста происходит правильный редирект.
        """
        group = TestCreateEditPostForm.test_group
        user_author = self.authorized_author
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Тестовый пост для проверки формы',
            'group': group.id,
            'image': uploaded,
        }
        count_post_before = Post.objects.count()
        
        print(form_data)
        print(settings.MEDIA_ROOT)

        response = user_author.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        print(response)

        # Для проверки выбирается последний добавленный пост
        # Порядок сортировки в модели по убыванию даты создания
        db_post = Post.objects.first()
        self.assertTrue(db_post)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), count_post_before + 1)
        self.assertEqual(db_post.text, form_data['text'])
        self.assertEqual(db_post.group, TestCreateEditPostForm.test_group)
        self.assertEqual(
            db_post.author, TestCreateEditPostForm.user_author
        )
        self.assertEqual(db_post.image, form_data['image'])

    def test_not_create_post_with_guest(self):
        """Проверка, что guest POST запросом не может создать пост.

        Методика проверки:
        - общее количество постов не изменилось.
        - гостевой клиент редиректится на главную.
        """
        group = TestCreateEditPostForm.test_group
        form_data = {
            'text': 'Тестовый пост для проверки формы',
            'group': group.id,
        }
        posts_count_before = Post.objects.count()
        response = self.client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('new_post')
        )
        self.assertEqual(Post.objects.count(), posts_count_before)

    def test_not_edit_post_with_user_not_author(self):
        """Проверка, что пользователь не может изменить чужой пост.

        Методика проверки:
        - общее количество постов не изменилось.
        - авторизованный клиент не автор редиректится на страницу поста
        - поля поста в БД не изменились
        """
        user_editor = User.objects.create(
            username='editor_not_owner_post'
        )
        authorized_editor = Client()
        authorized_editor.force_login(user_editor)
        group = TestCreateEditPostForm.test_group
        test_post = Post.objects.create(
            text='Test post text',
            author=TestCreateEditPostForm.user_author,
            group=group
        )
        test_post_id = test_post.id
        posts_count_before = Post.objects.count()
        another_group = Group.objects.create(
            title='Another test group',
            slug='anover-test-group'
        )

        form_data = {
            'text': 'Тестовый пост для проверки формы',
            'group': another_group.id,
        }

        response = authorized_editor.post(
            reverse(
                'post_edit', args=(test_post.author.username, test_post.id)
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'post', args=(test_post.author.username, test_post.id)
            )
        )
        db_post = Post.objects.get(id=test_post_id)
        self.assertEqual(Post.objects.count(), posts_count_before)
        self.assertNotEqual(db_post.text, form_data['text'])
        self.assertNotEqual(db_post.group, form_data['group'])

    def test_edit_post_user_author(self):
        """Проверка, что автор поста корректно редактирует пост.

        Методика проверки:
        - клиент редиректится на страницу поста
        - общее количество постов не изменилось.
        - поля поста получили новые корректные значения.
        """
        group = TestCreateEditPostForm.test_group
        test_post = Post.objects.create(
            text='Test post text',
            author=TestCreateEditPostForm.user_author,
            group=group
        )
        test_post_id = test_post.id
        posts_count_before = Post.objects.count()

        new_group = Group.objects.create(
            title='Тестовая группа №2',
            description='Более другая группа для теста',
            slug='test-2-slug'
        )

        form_data = {
            'text': 'Новый отредактированный текст поста',
            'group': new_group.id
        }

        response = self.authorized_author.post(
            reverse(
                'post_edit', args=(test_post.author.username, test_post.id)
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'post', args=(test_post.author.username, test_post.id)
            )
        )
        edited_post = Post.objects.get(id=test_post_id)
        self.assertEqual(Post.objects.count(), posts_count_before)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group, new_group)
        self.assertEqual(
            edited_post.author, TestCreateEditPostForm.user_author
        )
