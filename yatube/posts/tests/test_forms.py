from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class TestCreateEditPostForm(TestCase):
    """Проверка работы формы PostForm для создания поста."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_user = User.objects.create(
            username='test_user',
        )

        cls.user_author = User.objects.create(
            username='test_user_author',
        )

        cls.test_group = Group.objects.create(
            title='test_group_for_test_form',
            description='Description of test group',
            slug='slug_for_form'
        )


    def setUp(self):
        self.authorized_author = Client()
        author = TestCreateEditPostForm.user_author
        self.authorized_author.force_login(author)

        self.authorized_user = Client()
        user_user = TestCreateEditPostForm.authorized_user
        self.authorized_user.force_login(user_user)

        self.test_post = Post.objects.create(
            text='Test post text',
            author=TestCreateEditPostForm.user_author,
            group=TestCreateEditPostForm.test_group
        )
        self.test_post_id = self.test_post.id

    def test_create_post_user(self):
        """Проверка, что после валидации добавляется пост."""
        group = TestCreateEditPostForm.test_group

        form_data = {
            'text': 'Тестовый пост для проверки формы',
            'group': group.id,
        }
        count_post_before = Post.objects.count()

        response = self.authorized_user.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        # Для проверки выбирается последний добавленный пост
        # Порядок сортировки в модели по убыванию даты создания
        bd_post = Post.objects.first()
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), count_post_before + 1)
        self.assertEqual(bd_post.text, form_data['text'])
        self.assertEqual(bd_post.group, TestCreateEditPostForm.test_group)
        self.assertEqual(
            bd_post.author, TestCreateEditPostForm.authorized_user
        )

    def test_not_create_post_with_guest(self):
        form_data = {
            'text': 'Тестовый пост для проверки формы',
        }
        posts_count_before = Post.objects.count()
        response = self.client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('/new/')
        )
        self.assertEqual(Post.objects.count(), posts_count_before)

    def test_not_edit_post_with_user_not_author(self):
        """Проверка, что не автор поста не может использовать форму"""
        form_data = {
            'text': 'Тестовый пост для проверки формы',
        }

        db_post = Post.objects.get(id=self.test_post_id)

        response = self.authorized_user.post(
            reverse(
                'post_edit',
                kwargs={'username': db_post.author.username,
                        'post_id': db_post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'post', kwargs={'username': db_post.author.username,
                                'post_id': db_post.id}
            )
        )

    def test_edit_post_user_author(self):
        """Проверка, что для автора поста корректно используется форма"""
        # Вносимые в пост изменения
        form_data = {
            'text': 'Новый отредактированный текст поста',
            'group': ''
        }

        posts_count_before = Post.objects.count()
        db_post = Post.objects.get(id=self.test_post_id)

        post_before = {}
        post_before['text'] = db_post.text
        post_before['group'] = db_post.group

        self.authorized_author.post(
            reverse(
                'post_edit',
                kwargs={'username': db_post.author.username,
                        'post_id': db_post.id}
            ),
            data=form_data,
            follow=True
        )
        db_post = Post.objects.get(id=self.test_post_id)

        self.assertEqual(Post.objects.count(), posts_count_before)
        self.assertEqual(db_post.text, form_data['text'])
        self.assertEqual(db_post.group, None)
