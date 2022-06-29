# about/tests/tests_url.py
from http import HTTPStatus
from django.test import TestCase

url_templates_list = {
    '/about/author/': 'about/author.html',
    '/about/tech/': 'about/tech.html',
}


class StaticURLTests(TestCase):

    def test_about_page(self):
        """Проверка доступности адреса /about/."""
        for value in url_templates_list:
            with self.subTest(value=value):
                response = self.client.get(value)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_template(self):
        """Проверка шаблона для адреса /about/."""
        for value, expected_value in url_templates_list.items():
            with self.subTest(value=value):
                response = self.client.get(value)
                self.assertTemplateUsed(response, expected_value)
