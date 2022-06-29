# posts/tests/test_urls.py
from http import HTTPStatus
from django.test import TestCase, Client

from posts.models import User, Group, Post


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост для проверки',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю.."""
        url_list = (
            '/',
            '/group/test-slug/',
            '/profile/auth_user/',
            f'/posts/{PostsURLTests.post.id}/',
        )
        for url in url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_autorized_user(self):
        """страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_author(self):
        """страница posts/edit/ доступна автору."""
        response = self.authorized_client.get(
            f'/posts/{PostsURLTests.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        url_list = (
            f'/posts/{PostsURLTests.post.id}/edit/',
            '/create/',
        )
        for url in url_list:
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                target_url = f'/auth/login/?next={url}'
                self.assertRedirects(response, (target_url))

    def test_redirect_authorized_none_author(self):
        """Страница posts/edit/ перенаправит авторизованного
        пользователя (не автора) на страницу поста."""
        none_author = User.objects.create_user(username='auth_none_author')
        auth_none_author = Client()
        auth_none_author.force_login(none_author)
        url = f'/posts/{PostsURLTests.post.id}/edit/'
        response = auth_none_author.get(url, follow=True)
        target_url = f'/posts/{PostsURLTests.post.id}/'
        self.assertRedirects(response, target_url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_list = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth_user/': 'posts/profile.html',
            f'/posts/{PostsURLTests.post.id}/edit/': 'posts/create_post.html',
            f'/posts/{PostsURLTests.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template, in url_templates_list.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_unexisting_page(self):
        """Проверка несуществующей страницы"""
        response = self.client.get('/unexisting_page/')
        # Проверка, что статус ответа сервера - 404
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Проверка, что используется шаблон core/404.html
        self.assertTemplateUsed(response, 'core/404.html')
