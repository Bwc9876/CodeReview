from django.test import TestCase, override_settings
from django.urls import reverse

from Users.ldap_mock import LDAPMockAuthentication
from Users.models import User


class LogoutTest(TestCase):

    def test_logout(self):
        test_user = User.objects.create_user(username="test-user")
        self.client.force_login(test_user)
        self.client.get(reverse('logout'))
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, f"{reverse('login')}?next=%2F")


@override_settings(AUTHENTICATION_BACKENDS=['Users.ldap_mock.LDAPMockAuthentication'], LDAP_DOMAIN="example",
                   LDAP_BASE_CONTEXT="ou=ITP Users,dc=itp,dc=example")
class LDAPAuthTest(TestCase):
    url = reverse('login')

    def setUp(self) -> None:
        LDAPMockAuthentication.users = {
            'admin': {
                'password': "admin_password123",
                'first': "Bob",
                'last': "Bobberson",
                'ou': None
            },
            'user_am': {
                'password': "am_user_password123",
                'first': "AMBob",
                'last': "AMBobberson",
                'ou': "AM"
            },
            'user_pm': {
                'password': "pm_user_password123",
                'first': "PMBob",
                'last': "PMBobberson",
                'ou': "PM"
            },
            'user_has_empty': {
                'password': "user_empty_password123",
                'first': "",
                'last': "",
                'ou': "AM"
            }
        }

    def test_admin_login(self) -> None:
        self.client.post(self.url, {'username': "admin", "password": "admin_password123"})
        new_user = User.objects.get(username="example\\admin")
        self.assertEqual(new_user.first_name, "Bob")
        self.assertEqual(new_user.last_name, "Bobberson")
        self.assertEqual(new_user.session, User.Session.AM)
        self.assertTrue(new_user.is_superuser)

    def test_student_am_login(self) -> None:
        self.client.post(self.url, {'username': "user_am", 'password': "am_user_password123"})
        new_user = User.objects.get(username="example\\user_am")
        self.assertEqual(new_user.first_name, "AMBob")
        self.assertEqual(new_user.last_name, "AMBobberson")
        self.assertEqual(new_user.session, User.Session.AM)
        self.assertFalse(new_user.is_superuser)

    def test_student_pm_login(self) -> None:
        self.client.post(self.url, {'username': "user_pm", 'password': "pm_user_password123"})
        new_user = User.objects.get(username="example\\user_pm")
        self.assertEqual(new_user.first_name, "PMBob")
        self.assertEqual(new_user.last_name, "PMBobberson")
        self.assertEqual(new_user.session, User.Session.PM)
        self.assertFalse(new_user.is_superuser)

    def test_has_empty(self) -> None:
        self.client.post(self.url, {'username': "user_has_empty", 'password': "user_empty_password123"})
        new_user = User.objects.get(username="example\\user_has_empty")
        self.assertEqual(new_user.first_name, "")
        self.assertEqual(new_user.last_name, "")

    def test_invalid(self) -> None:
        response = self.client.post(self.url, {'username': "invalid_user", 'password': "invalid_password"})
        self.assertEqual(len(response.context.get('form').non_field_errors()), 1)

    def tearDown(self) -> None:
        LDAPMockAuthentication.users = []


@override_settings(AUTHENTICATION_BACKENDS=['Users.ldap_mock.LDAPMockAuthentication'], LDAP_DOMAIN="example",
                   LDAP_BASE_CONTEXT="ou=ITP Users,dc=itp,dc=example")
class UserCleanupTest(TestCase):
    url = reverse('user-cleanup')

    def setUp(self) -> None:
        LDAPMockAuthentication.users = {
            'admin': {
                'password': "admin_password123",
                'first': "First",
                'last': "Last",
                'ou': None
            },
            'student': {
                'password': "student_password123",
                'first': "SFirst",
                'last': "SLast",
                'ou': "AM"
            }
        }
        self.client.post(reverse('login'), {'username': 'admin', 'password': "admin_password123"})
        self.client.post(reverse('login'), {'username': 'student', 'password': "student_password123"})
        self.old_user = User.objects.create_user(username='example\\old_user')
        self.old_user.set_unusable_password()
        self.old_user.save()
        self.student = User.objects.get(username="example\\student")
        self.client.force_login(User.objects.get(username="example\\admin"))

    def test_cleanup_users(self):
        response = self.client.post(self.url, {'userPassword': "admin_password123"})
        self.assertRedirects(response, reverse('user-list'))
        self.assertFalse(User.objects.filter(username="example\\old_user").exists())
        self.assertTrue(User.objects.filter(username="example\\student").exists())

    def test_no_password(self):
        self.client.post(self.url, {'userPassword': ""})
        self.assertTrue(User.objects.filter(username="example\\old_user").exists())
        self.assertTrue(User.objects.filter(username="example\\student").exists())

    def test_password_wrong(self):
        self.client.post(self.url, {'userPassword': "wrong password"})
        self.assertTrue(User.objects.filter(username="example\\old_user").exists())
        self.assertTrue(User.objects.filter(username="example\\student").exists())

    def test_insufficient_perms(self):
        self.client.force_login(self.student)
        self.client.post(self.url, {'userPassword': "student_password123"})
        self.assertTrue(User.objects.filter(username="example\\old_user").exists())
        self.assertTrue(User.objects.filter(username="example\\student").exists())

    def tearDown(self) -> None:
        LDAPMockAuthentication.users = []
