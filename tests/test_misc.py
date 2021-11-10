from django.test import TestCase, Client
from django.urls import reverse

from Users.models import User


class UserSetupTest(TestCase):

    def get_url(self, user):
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
        self.assertEqual(User.objects.get(id=self.admin.id).email, "admin@admin.example.com")

    def test_user_edit(self):
        self.student_c.post(self.get_url(self.student), {'email': '985'})
        self.assertEqual(User.objects.get(id=self.student.id).email, "johdoe985@example.com")

    def test_student_length_check(self):
        response = self.student_c.post(self.get_url(self.student), {'email': '1'})
        self.assertEqual(response.context.get('form').errors.get('email')[0], "Please enter 3 digits")
        response = self.student_c.post(self.get_url(self.student), {'email': '1111'})
        self.assertEqual(response.context.get('form').errors.get('email')[0], "Please enter 3 digits")

    def test_student_numeric_check(self):
        response = self.student_c.post(self.get_url(self.student), {'email': 'abc'})
        self.assertEqual(response.context.get('form').errors.get('email')[0], "Must be a number")


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
