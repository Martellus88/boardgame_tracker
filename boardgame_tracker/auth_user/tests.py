from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from services.queries import create_and_save_user

User = get_user_model()


class TestAuthUserClient(TestCase):

    def setUp(self):
        self.bob = create_and_save_user(password='123', username='bob', email='bob@ex.com')

    def tearDown(self):
        self.bob.delete()

    def test_get_register_page(self):
        resp = self.client.get(reverse('auth_user:register'))
        self.assertEqual(resp.status_code, 200)

    def test_post_register(self):
        resp = self.client.post(reverse('auth_user:register'),
                                {'username': 'john',
                                 'password1': 'qwe123Qqq',
                                 'password2': 'qwe123Qqq',
                                 'email': 'john@ex.com'
                                 }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bg_tracker/index.html')
        assert User.objects.get(email='john@ex.com')

    def test_post_register_email_exists(self):
        resp = self.client.post(reverse('auth_user:register'),
                                {'username': 'john',
                                 'password1': 'qwe123Qqq',
                                 'password2': 'qwe123Qqq',
                                 'email': 'bob@ex.com'
                                 })
        self.assertTemplateUsed(resp, 'registration/signup.html')
        self.assertIn('email already exists', resp.context['form'].errors['email'])

    def test_login(self):
        resp = self.client.login(email='bob@ex.com', password='123')
        self.assertTrue(resp)
