from random import randint

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()




class YaTbPaginationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.COUNT_ITEMS_FOR_PAGINATOR = 10
        # Создаём записи в БД
        # Групп больше на 3 чем количество объектов пагинатора на страницу
        for i in range(1, int(cls.COUNT_ITEMS_FOR_PAGINATOR + 5)):
            cls.group = Group.objects.create(
                title='Тестовая подборка записей №' + str(i),
                description='Тестирующая контекст подборка №' + str(i),
                slug='test-slug' + str(i),
            )
            cls.group.save()

        # Постов больше на 3 чем количество объектов пагинатора на страницу
        for i in range(1, int(cls.COUNT_ITEMS_FOR_PAGINATOR + 5)):
            cls.test_post = Post.objects.create(
                author=User.objects.create(username='Test_user' + str(i)),
                text='Проверочный текст для поста проверки контекста' + str(i),
            )
            # каждый третий пост без группы
            tmp_ind_div3 = (i + 2) % 3
            if tmp_ind_div3:
                group = Group.objects.get(id=tmp_ind_div3)
                cls.test_post.group = group
            cls.test_post.save()

        cls.post_count = Post.objects.all().count()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='CoherentuS')
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверка словаря контекста главной страницы
    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом.

        Ожидаемый контекст должен содержать словарь page с кол-вом постов,
        прописанным при конструировании paginator-а. Посты должны содержать
        поля post.author post.text post.group . Показ всего содержимого
        'index' не требует и не зависит от авторизации пользователя.
        На метод "POST" не реагирует.
        """
        response = self.guest_client.get(reverse('index'))
        posts_per_page = response.context.get('page').object_list
        self.assertEqual(len(posts_per_page),
                         YaTbPagesTests.COUNT_ITEMS_FOR_PAGINATOR,
                         'Количество постов не равно пагинатору')
        """Количество постов, выводимых на странице равно пагинатору"""

        for post in posts_per_page:            
            self.assertTrue(hasattr(post, 'author') in response.context,
                            'Нет post.author в context шаблона index')
            self.assertTrue(hasattr(post, 'text') in response.context,
                            'Нет post.author в context шаблона index')
            self.assertTrue(hasattr(post, 'group') in response.context,
                            'Нет post.author в context шаблона index')

# Проверка словаря контекста страницы группы
    def test_group_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом.

        Ожидаемый контекст должен содержать словарь page с кол-вом постов,
        прописанным при конструировании paginator-а. Посты должны содержать
        поля post.author post.text post.group . Показ всего содержимого
        'group' не требует и не зависит от авторизации пользователя.
        На метод "POST" не реагирует.
        """
        # группа имеет slug. slug имеет вид slug='test-slug' + str(i),
        # где 1 < i < int(cls.COUNT_ITEMS_FOR_PAGINATOR * 2.5 + 1),
        # для COUNT_ITEMS_FOR_PAGINATOR == 10  i == 26
        # тестовых групп int(cls.COUNT_ITEMS_FOR_PAGINATOR * 2.5 + 1)
        # тестируем первую, последнюю и рандомную группу
        first_slug = 'test-slug' + str(1)
        last_i = int(YaTbPagesTests.COUNT_ITEMS_FOR_PAGINATOR * 2.5 + 1)
        last_slug = 'test-slug' + str(last_i)
        while True:
            random_i = randint(1, last_i)
            if random_i != 1 and random_i != last_i:
                break
        random_slug = 'test-slug' + str(random_i)


        response = self.guest_client.get(
            reverse('group', kwargs={'slug': first_slug}))
        posts_per_page = response.context.get('page').object_list
        self.assertEqual(len(posts_per_page),
                         YaTbPagesTests.COUNT_ITEMS_FOR_PAGINATOR,
                         'Количество постов не равно пагинатору')
        """Количество постов, выводимых на странице равно пагинатору"""

        for post in posts_per_page:            
            self.assertTrue(hasattr(post, 'author') in response.context,
                            'Нет post.author в context шаблона index')
            self.assertTrue(hasattr(post, 'text') in response.context,
                            'Нет post.author в context шаблона index')
            self.assertTrue(hasattr(post, 'group') in response.context,
                            'Нет post.author в context шаблона index')


