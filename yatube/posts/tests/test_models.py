from datetime import date

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class YaTbSmokeTst(TestCase):

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

        self.test_user = User(
            username='test_user',
            first_name='first_test_name',
            last_name='last_name_test',
            email='test@yatube.ru'
        )

        self.test_group = Group(
            title='test_group',
            description='test_group_description',
            slug=''
        )

        self.test_post = Post(
            text='test post text for test __str__',
            author=self.test_user
        )

    def test_smoke(self):
        """'Дымовой тест. Проверка, что на запрос '/' ответ 200."""
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(
            response.status_code, 200,
            'Гость не получает стартовую страницу'
        )

    def test_group_str(self):
        """Проверка, что Group.__str__ возвращает название группы."""
        self.assertEqual(
            f'{self.test_group}', 'test_group',
            'Метод Group.__str__ не работает ожидаемым образом'
        )

    def test_post_str(self):
        """Проверка, что Post.__str__ возвращает первые 15 символов поста."""
        self.assertEqual(
            f'{self.test_post}', 'test post text ',
            'Метод Post.__str__ не работает ожидаемым образом'
        )


class YaTube_Test_Models(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаём тестовый набор
        # атрибутов класса
        cls.test_user = User.objects.create(
            username='test_user',
            first_name='first_test_name',
            last_name='last_name_test',
            email='test@yatube.ru'
        )

        cls.test_group = Group.objects.create(
            title='test_group',
            description='test_group_description',
            slug=''
        )

        cls.test_post = Post.objects.create(
            text='test post text for test __str__',
            author=cls.test_user,
            group=cls.test_group,
            pub_date=date.today()
        )

    def test_verbose_name_model_group(self):
        """Провека, что verbose_name в полях Group совпадает с ожидаемым."""
        group = YaTube_Test_Models.test_group
        field_verboses = {
            'title': 'Название подборки',
            'description': 'Описание подборки',
            'slug': 'Часть адресной строки для подборки',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text_model_group(self):
        """Проверка, что help_text в полях Group совпадает с ожидаемым."""
        group = YaTube_Test_Models.test_group
        field_help_texts = {
            'title': 'Группа, сообщество, подборка записей, суть одна, '
            'в этом месте собраны сообщения, имеющие некую общность. '
            'Название подборки призвано её отражать',
            'description': 'Краткое описание принципов объединения записей в'
            ' подборку, тематика и основные правила поведения',
            'slug': 'Укажите адрес для страницы подборки. Используйте '
            'только латиницу, цифры, дефисы и знаки подчёркивания',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

    def test_verbose_name_model_post(self):
        """Проверка, что verbose_name в полях Post совпадает с ожидаемым."""
        post = YaTube_Test_Models.test_post
        field_verboses = {
            'text': 'Текст записи',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Подборка записей'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)
