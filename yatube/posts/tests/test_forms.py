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

    def test_create_post_user(self):
        """Проверка, что после валидации добавляется пост.

        Методика проверки:
        - общее количество постов увеличилось на единицу.
        - поля созданного поста соответствуют полям формы.
        - после создания поста происходит правильный редирект.
        """
        group = TestCreateEditPostForm.test_group
        user_author = self.authorized_author

        form_data = {
            'text': 'Тестовый пост для проверки формы',
            'group': group.id,
        }
        count_post_before = Post.objects.count()

        response = user_author.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

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

        form_data = {
            'text': 'Тестовый пост для проверки формы',
            'group': group.id,
        }

        db_post = Post.objects.get(id=test_post_id)

        response = authorized_editor.post(
            reverse(
                'post_edit', args=(db_post.author.username, db_post.id)
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'post', args=(db_post.author.username, db_post.id)
            )
        )
        self.assertEqual(Post.objects.count(), posts_count_before)
        self.assertEqual(test_post, Post.objects.get(id=test_post_id))
        self.assertEqual(test_post.text, db_post.text)
        self.assertEqual(test_post.group, db_post.group)

    def test_edit_post_user_author(self):
        """Проверка, что автор поста корректно редактирует пост.

        Методика проверки:
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
        db_post = Post.objects.get(id=test_post_id)
        posts_count_before = Post.objects.count()

        new_group = Group.objects.create(
            title='Тестовая группа №2',
            description='Более другая группа для теста',
            slug='test-2-slug'
        )

        # Вносимые в пост изменения
        form_data = {
            'text': 'Новый отредактированный текст поста',
            'group': new_group.id
        }

        self.authorized_author.post(
            reverse(
                'post_edit', args=(db_post.author.username, db_post.id)
            ),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.get(id=test_post_id)
        self.assertEqual(Post.objects.count(), posts_count_before)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
