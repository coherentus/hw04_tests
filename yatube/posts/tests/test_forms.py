from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class TestCreatePostForm(TestCase):
    """Проверка работы формы PostForm для создания поста."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.autorized_user = User.objects.create_user(
            username = 'test_user',
            password = '12345678'
        )
        
        cls.test_group = Group.objects.create(
            title = 'test_group_for_test_form',
            description = 'Description of test group',
            slug = 'slug_for_form'
        )
        
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        user = TestCreatePostForm.autorized_user
        self.authorized_client.force_login(user)
    
    def test_create_post_user(self):
        """Проверка, что после валидации добавляется пост."""        
        group = TestCreatePostForm.test_group
        
        form_data = {
            'text': 'Тестовый пост для проверки формы',
            'group': group.id,
        }
        if Post.objects.count():
            Post.objects.all().delete()
        
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        bd_post = Post.objects.first()
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(bd_post.text, form_data['text'])
        self.assertEqual(bd_post.group.id, form_data['group'])
        self.assertEqual(
            bd_post.author, TestCreatePostForm.autorized_user
        )


    def test_not_create_post_with_guest(self):
        form_data = {
            'text': 'Тестовый пост для проверки формы',            
        }
        guest_client = Client()
        posts_count = Post.objects.count()
        response = guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/new/')
        self.assertEqual(Post.objects.count(), posts_count)








"""Post.objects.filter(
                slug=self.test_class.test_group.slug,
                text='Тестовый пост для проверки формы',                
                ).exists()"""
