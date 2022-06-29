# posts/tests/test_views.py
from linecache import cache
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms


from posts.models import User, Group, Post, Comment, Follow
from posts.views import POSTS_COUNT

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост для проверки',
            image=SimpleUploadedFile(
                name='test.gif',
                content=test_gif,
                content_type='image/gif'
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'auth_user'}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста главной страницы
    def test_index_page_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        test_post = response.context['page_obj'][0]
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.image, self.post.image)

    # Проверка словаря контекста group_list
    def test_group_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'})
        )
        test_group = response.context['group']
        test_post = response.context['page_obj'][0]
        self.assertEqual(test_group.slug, self.group.slug)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.image, self.post.image)

    # Проверка словаря контекста profile
    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth_user'})
        )
        test_author = response.context['author']
        test_post = response.context['page_obj'][0]
        self.assertEqual(test_author, self.user)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.image, self.post.image)

    # Проверка словаря контекста post_detail
    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        test_post = response.context['post']
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.image, self.post.image)

        form_field = response.context['form'].fields['text']
        self.assertIsInstance(form_field, forms.fields.CharField)

    # Проверка словаря контекста create_post
    def test_create_post_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
        self.assertIsInstance(form_field, expected)

    # Проверка словаря контекста edit_post
    def test_edit_post_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        is_edit = response.context['is_edit']
        self.assertTrue(is_edit)
        # Словарь ожидаемых типов полей формы:
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
        self.assertIsInstance(form_field, expected)


class PostsWithoutGroupTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверка словаря контекста group_list(без группы)
    def test_group_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'testslug'})
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):

    TEST_POSTS_COUNT = 13

    templates_pages_names = (
        reverse('posts:index'),
        reverse('posts:group_list', kwargs={'slug': 'testslug'}),
        reverse('posts:profile', kwargs={'username': 'auth_user'}),
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание группы',
        )
        for num_post in range(cls.TEST_POSTS_COUNT):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Тестовый пост для проверки № %s' % (num_post),
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверка: количество постов на первой странице равно 10.
    def test_first_page_contains_ten_records(self):
        """Проверка постов на первой странице."""
        for reverse_name in self.templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    POSTS_COUNT
                )

    # Проверка: на второй странице должно быть три поста.
    def test_second_page_contains_three_records(self):
        """Проверка постов на второй странице."""
        for reverse_name in self.templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse_name, {'page': 2})
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.TEST_POSTS_COUNT - POSTS_COUNT
                )


class CacheTests(TestCase):

    def test_cache_index_page(self):
        """Проверка кэширования главной страницы"""
        cache.clear()
        user = User.objects.create_user(username='user')
        post = Post.objects.create(
            author=user,
            text='Тестовый пост для проверки',
        )
        response = self.client.get(reverse('posts:index'))
        post.delete()
        response_after_del = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_after_del.content)


class CommentsAddTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment_none_authorized_client(self):
        """проверка создания комментария неавторизованным пользователем."""
        comment_count = Comment.objects.count()
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': 'новый комментарий'},
            follow=True
        )
        # Проверяем, что число комментариев не изменилось
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_add_comment_authorized_client(self):
        """проверка создания комментария авторизованным пользователем."""
        comment_count = Comment.objects.count()
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': 'новый комментарий'},
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        # Проверяем, увеличилось ли число комментариев
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        # Проверяем, что создалась запись
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                post=self.post,
                text='новый комментарий',
            ).exists()
        )


class FollowTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.author = User.objects.create_user(username='author')
        cls.unfollow = User.objects.create_user(username='unfollow')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.unfollow_client = Client()
        self.unfollow_client.force_login(self.unfollow)

    def test_following_auth_user(self):
        """Авторизованный пользователь может подписываться на других"""
        count = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        # Проверяем, увеличилось ли число записей
        self.assertEqual(Follow.objects.count(), count + 1)
        # Проверяем, что создалась подписка
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author,
            ).exists()
        )

    def test_unfollowing_auth_user(self):
        """Авторизованный пользователь может отписаться."""
        Follow.objects.create(
            user=self.user,
            author=self.author,
        )
        count = Follow.objects.count()
        # отписываемся
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )
        # Проверяем, уменьшилось ли число записей
        self.assertEqual(Follow.objects.count(), count - 1)
        # Проверяем, что подписки нет
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author,
            ).exists()
        )

    def test_post_exists_for_follower(self):
        """Пост появился в ленте у подписчика."""
        post = Post.objects.create(author=self.author, text='тестовый текст')
        # создаем подписку
        Follow.objects.create(
            user=self.user,
            author=self.author,
        )
        # пост появился у подписчика
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertIn(post, response.context['page_obj'])

    def test_post_no_exists_for_unfollower(self):
        """Пост отсутствует в ленте у неподписчика."""
        post = Post.objects.create(author=self.author, text='тестовый текст')
        # создаем подписку
        Follow.objects.create(
            user=self.user,
            author=self.author,
        )
        # пост отсутствует у постороннего
        response = self.unfollow_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
        self.assertNotIn(post, response.context['page_obj'])
