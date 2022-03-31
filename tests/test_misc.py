from django.conf import settings
from django.test import TestCase, RequestFactory
from django.urls import reverse

from Main.views import error_500_handler
from Users.models import User
from tests.testing_base import BaseCase


class UserSetupTest(BaseCase):

    @staticmethod
    def get_url(user):
        return reverse('user-setup', kwargs={'pk': user.id})

    test_users = BaseCase.USER_SINGLE_STUDENT

    test_rubric = False
    test_review = False

    def assertEmailError(self, response, message):
        self.assertFormError(response, 'form', 'email', [message])

    def post_setup(self, user, email):
        return self.post(user, reverse('user-setup', kwargs={'pk': self.users[user].id}), {'email': email})

    def setUp(self) -> None:
        super(UserSetupTest, self).setUp()
        self.users['test-user'].email = ""
        self.set_user_full_name('test-user', "John", "Doe")
        self.users['test-user'].save()
        self.users['super'].email = ""
        self.users['super'].save()

    def test_redirects(self):
        response = self.get('super', reverse('home'))
        self.assertEqual(response.status_code, 302)
        response = self.get('test-user', reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_admin_edit(self):
        self.post_setup('super', 'admin')
        self.assertEqual(User.objects.get(id=self.users['super'].id).email, f"admin@{settings.EMAIL_ADMIN_DOMAIN}")

    def test_user_edit(self):
        self.post_setup('test-user', '985')
        self.assertEqual(User.objects.get(id=self.users['test-user'].id).email, f"johdoe985@{settings.EMAIL_DOMAIN}")

    def test_student_length_check(self):
        response = self.post_setup('test-user', '1')
        self.assertEmailError(response, "Must be three digits")
        response = self.post_setup('test-user', '1111')
        self.assertEmailError(response, "Must be three digits")

    def test_less_than_100_but_still_over_0(self):
        self.post_setup('test-user', '025')
        self.assertEqual(User.objects.get(id=self.users['test-user'].id).email, f"johdoe025@{settings.EMAIL_DOMAIN}")

    def test_student_numeric_check(self):
        response = self.post_setup('test-user', 'abc')
        self.assertEmailError(response, "Must be three digits")

    def test_student_decimal_check(self):
        response = self.post_setup('test-user', '1.1')
        self.assertEmailError(response, "Must be three digits")

    def test_student_negative_check(self):
        response = self.post_setup('test-user', '-99')
        self.assertEmailError(response, "Must be three digits")


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
