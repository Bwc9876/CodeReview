from uuid import uuid4

from django.contrib.messages import get_messages
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
                   LDAP_BASE_CONTEXT="ou=ITP Users,dc=itp,dc=example", LDAP_URL="example-server")
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

    def test_change(self) -> None:
        self.client.post(self.url, {'username': "user_pm", 'password': "pm_user_password123"})
        user_pm = User.objects.get(username="example\\user_pm")
        user_pm.first_name = "DiffName"
        user_pm.last_name = "DiffLastName"
        user_pm.session = User.Session.AM
        user_pm.save()
        self.client.post(self.url, {'username': "user_pm", 'password': "pm_user_password123"})
        updated_user = User.objects.get(username=f"example\\user_pm")
        self.assertEqual(updated_user.first_name, "PMBob")
        self.assertEqual(updated_user.last_name, "PMBobberson")
        self.assertEqual(updated_user.session, User.Session.PM)

    def test_no_user(self) -> None:
        user = LDAPMockAuthentication().get_user(str(uuid4()))
        self.assertIsNone(user)

    def test_no_email(self) -> None:
        response = self.client.post(self.url, {'username': "admin", "password": "admin_password123"})
        self.assertEqual(response.url, reverse('user-setup',
                                               kwargs={'pk': User.objects.get(username="example\\admin").id}))

    def test_has_email(self) -> None:
        self.client.post(self.url, {'username': "admin", "password": "admin_password123"})
        admin = User.objects.get(username=f"example\\admin")
        admin.email = "admin@admin.example.com"
        admin.save()
        response = self.client.post(self.url, {'username': "admin", "password": "admin_password123"})
        self.assertEqual(response.url, reverse("home"))

    def test_invalid(self) -> None:
        response = self.client.post(self.url, {'username': "invalid_user", 'password': "invalid_password"})
        self.assertEqual(len(response.context.get('form').non_field_errors()), 1)

    @override_settings(AUTHENTICATION_BACKENDS=['Users.ldap_auth.LDAPAuthentication'])
    def test_cant_connect(self) -> None:
        response = self.client.post(self.url, {'username': "admin", 'password': "admin_password123"})
        self.assertIn("There was an error contacting the auth server, please try again later.",
                      [m.message for m in response.context.get('messages', [])])

    def tearDown(self) -> None:
        LDAPMockAuthentication.users = []


@override_settings(AUTHENTICATION_BACKENDS=['Users.ldap_mock.LDAPMockAuthentication'], LDAP_DOMAIN="example",
                   LDAP_BASE_CONTEXT="ou=ITP Users,dc=itp,dc=example", LDAP_URL="example-server")
class UserCleanupTest(TestCase):
    url = reverse('user-cleanup')

    def assertMessage(self, response, message):
        self.assertIn(message, [m.message for m in get_messages(response.wsgi_request)])

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
        self.admin = User.objects.get(username="example\\admin")
        self.client.force_login(self.admin)

    def test_cleanup_users(self):
        self.client.post(self.url, {'userPassword': "admin_password123"})
        self.assertFalse(User.objects.filter(username="example\\old_user").exists())
        self.assertTrue(User.objects.filter(username="example\\student").exists())

    def test_no_password(self):
        response = self.client.post(self.url, {'userPassword': ""})
        self.assertTrue(User.objects.filter(username="example\\old_user").exists())
        self.assertTrue(User.objects.filter(username="example\\student").exists())
        self.assertMessage(response, "Please provide a password")

    def test_password_wrong(self):
        response = self.client.post(self.url, {'userPassword': "wrong password"})
        self.assertTrue(User.objects.filter(username="example\\old_user").exists())
        self.assertTrue(User.objects.filter(username="example\\student").exists())
        self.assertMessage(response, "The password you provided was incorrect, please check it and try again.")

    def test_insufficient_perms(self):
        self.student.is_superuser = True
        self.student.save()
        self.client.force_login(self.student)
        response = self.client.post(self.url, {'userPassword': "student_password123"})
        self.assertTrue(User.objects.filter(username="example\\old_user").exists())
        self.assertTrue(User.objects.filter(username="example\\student").exists())
        self.assertMessage(response, "You lack permissions to perform this action.")

    @override_settings(AUTHENTICATION_BACKENDS=['Users.ldap_auth.LDAPAuthentication'])
    def test_cant_connect(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {'userPassword': "admin_password123"})
        self.assertTrue(User.objects.filter(username="example\\old_user").exists())
        self.assertTrue(User.objects.filter(username="example\\student").exists())
        self.assertMessage(response, "Can't connect to ActiveDirectory, please try again later.")

    def tearDown(self) -> None:
        LDAPMockAuthentication.users = []
