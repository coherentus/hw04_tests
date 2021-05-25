from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class ModelsStrTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(
            username='Toster'
        )

        cls.test_group = Group.objects.create(
            title='Title test group',
            description='Description test group'
        )
        cls.test_post = Post.objects.create(
            text='Самый тестовый из постов',
            author=cls.test_user
        )

        cls.test_array = (
            (cls.test_group, cls.test_group.title),
            (cls.test_post, cls.test_post.text[:15]),
        )

    def test_models_str_return(self):
        """Проверка, что методы __str__ моделей работают корректно."""
        for tuple_elem in ModelsStrTests.test_array:
            model_name, str_value = tuple_elem
            with self.subTest(model_name=model_name):
                self.assertEqual(str(model_name), str_value)
