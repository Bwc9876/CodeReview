from django.test import TestCase, RequestFactory
from django.urls import reverse

from Users.models import User
from tests.testing_base import BaseCase
from Main.views import error_500_handler


class TestSetup(BaseCase):

    test_users = BaseCase.USER_STUDENT_REVIEWER
    test_review = False

    def test_setup(self):
        response = self.clients["student"].post(reverse('user-setup', kwargs={'pk': self.users["student"].id}), {'session': "PM"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.get(pk=self.users["student"].id).session, User.Session.PM)


class TestErrors(TestCase):

    def test_404(self):
        response = self.client.get(reverse("error", kwargs={'type': 404}))
        self.assertIn("errors/404.html", response.template_name)

    def test_403(self):
        response = self.client.get(reverse("error", kwargs={'type': 403}))
        self.assertIn("errors/403.html", response.template_name)

    def test_500(self):
        response = self.client.get(reverse("error", kwargs={'type': 500}))
        self.assertIn("errors/500.html", response.template_name)

    def test_500_func(self):
        request = RequestFactory().get('/error/500')
        response = error_500_handler(request)
        self.assertIn("errors/500.html", response.template_name)

    def test_404_post(self):
        response = self.client.post(reverse('error', kwargs={'type': 404}))
        self.assertEqual(response.templates[0].name, 'errors/404.html')

    def test_403_post(self):
        response = self.client.post(reverse('error', kwargs={'type': 403}))
        self.assertEqual(response.templates[0].name, 'errors/403.html')

    def test_500_post(self):
        response = self.client.post(reverse('error', kwargs={'type': 500}))
        self.assertEqual(response.templates[0].name, 'errors/500.html')

    def test_invalid_type(self):
        response = self.client.get(reverse("error", kwargs={'type': 111}))
        self.assertIn("errors/404.html", response.template_name)
