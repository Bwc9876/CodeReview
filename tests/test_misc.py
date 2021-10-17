from django.test import TestCase, Client
from django.urls import reverse

from Users.models import User


class LogoutTest(TestCase):

    def test_logout(self):
        test_user = User.objects.create_user(username="test-user")
        client = Client()
        client.force_login(test_user)
        response = client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('logout-done'))
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login') + f"?next={reverse('home')}")
