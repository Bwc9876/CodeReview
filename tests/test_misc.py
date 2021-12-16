import os

from django.conf import settings
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from CodeReview.load_env import load_to_env, get_env
from Main.views import error_500_handler
from Users.models import User


class EnvLoadTest(TestCase):

    def setUp(self) -> None:
        with open('env_test.ps1', 'w+') as file:
            file.writelines([
                '#This is a comment, it shouldn\'t load\n',
                '$Env:TEST_VAR=\"Hello, World!\"\n',
                '$Env:EQUAL=\"hi=hi\"\n'
            ])

    def test_get(self) -> None:
        results = get_env('env_test.ps1')
        self.assertDictEqual(results, {'TEST_VAR': "Hello, World!", 'EQUAL': "hi=hi"})

    def test_load(self) -> None:
        load_to_env('env_test.ps1')
        self.assertEqual(os.getenv('TEST_VAR'), "Hello, World!")

    def test_no_file(self) -> None:
        results = get_env("not_a_file.ps1")
        self.assertIsNone(results)

    def tearDown(self) -> None:
        if os.path.exists('env_test.ps1'):
            os.remove('env_test.ps1')


class UserSetupTest(TestCase):

    @staticmethod
    def get_url(user):
        return reverse('user-setup', kwargs={'pk': user.id})

    def create_users(self):
        self.admin = User.objects.create_superuser('admin')
        self.student = User.objects.create_user('student', first_name="John", last_name="Doe")

    def create_clients(self):
        self.admin_c = Client()
        self.admin_c.force_login(self.admin)
        self.student_c = Client()
        self.student_c.force_login(self.student)

    def setUp(self) -> None:
        self.create_users()
        self.create_clients()

    def test_redirects(self):
        response = self.admin_c.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        response = self.student_c.get(reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_admin_edit(self):
        self.admin_c.post(self.get_url(self.admin), {'email': "admin"})
        self.assertEqual(User.objects.get(id=self.admin.id).email, f"admin@{settings.EMAIL_ADMIN_DOMAIN}")

    def test_user_edit(self):
        self.student_c.post(self.get_url(self.student), {'email': '985'})
        self.assertEqual(User.objects.get(id=self.student.id).email, f"johdoe985@{settings.EMAIL_DOMAIN}")

    def test_student_length_check(self):
        response = self.student_c.post(self.get_url(self.student), {'email': '1'})
        self.assertEqual(response.context.get('form').errors.get('email')[0], "Please enter 3 digits")
        response = self.student_c.post(self.get_url(self.student), {'email': '1111'})
        self.assertEqual(response.context.get('form').errors.get('email')[0], "Please enter 3 digits")

    def test_student_numeric_check(self):
        response = self.student_c.post(self.get_url(self.student), {'email': 'abc'})
        self.assertEqual(response.context.get('form').errors.get('email')[0], "Must be a number")

    def test_student_decimal_check(self):
        response = self.student_c.post(self.get_url(self.student), {'email': '1.1'})
        self.assertEqual(response.context.get('form').errors.get('email')[0], "Must be a number")

    def test_student_negative_check(self):
        response = self.student_c.post(self.get_url(self.student), {'email': '-99'})
        self.assertEqual(response.context.get('form').errors.get('email')[0], "Must be between 100-999")


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
