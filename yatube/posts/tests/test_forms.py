from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class YaTb_test_create_PostForm(TestCase):
    """Проверка создания работы формы для создания поста."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.autorized_user = User.objects.create(
            username='test_user',
            password='12345678'
        )

        cls.test_group = Group.objects.create(
            title='test_group_for_test_form',
            description='Description of test group',
            slug='slug_for_form'
        )

        cls.form = PostForm()

    def setUp(self):
        self.test_class = YaTb_test_create_PostForm

        # неавторизованный клиент
        self.guest_client = Client()

        # авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_class.autorized_user)

    def test_create_post(self):
        """Проверка, что после валидации добавляется пост."""

        post_count_before = Post.objects.count()

        form_data = {
            'text': 'Тестовый пост для проверки формы',
            'group': YaTb_test_create_PostForm.test_group.id
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('index'))

        self.assertEqual(Post.objects.count(), post_count_before + 1)

        self.assertTrue(
            Post.objects.filter(
                group=self.test_class.test_group.id,
                text='Тестовый пост для проверки формы').exists()
        )
