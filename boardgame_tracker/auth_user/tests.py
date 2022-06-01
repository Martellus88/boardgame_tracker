from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestAuthUserClient(TestCase):

    def setUp(self):
        self.bob = User.objects.create(username='bob', email='bob@ex.com', password='123')

    def test_get_register_page(self):
        resp = self.client.get(reverse('auth_user:register'))
        self.assertEqual(resp.status_code, 200)

    def test_post_register(self):
        resp = self.client.post(reverse('auth_user:register'),
                                {'username': 'john',
                                 'password1': 'qwe123Qqq',
                                 'password2': 'qwe123Qqq',
                                 'email': 'john@ex.com'
                                 })
        self.assertEqual(resp.status_code, 302)
        assert User.objects.get(email='john@ex.com')

    def test_post_register_email_exists(self):
        resp = self.client.post(reverse('auth_user:register'),
                                {'username': 'john',
                                 'password1': 'qwe123Qqq',
                                 'password2': 'qwe123Qqq',
                                 'email': 'bob@ex.com'
                                 })
        self.assertIn('email already exists', resp.context['form'].errors['email'])
