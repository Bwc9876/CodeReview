from django.test import TestCase, RequestFactory
from django.urls import reverse

from Main.views import error_500_handler
from Users.models import User
from tests.testing_base import BaseCase


class UserSetupTest(BaseCase):
    test_users = BaseCase.USER_SINGLE_STUDENT
    test_review = False

    def test_get_user_setup(self):
        self.get(
            "test-user",
            reverse("user-setup", kwargs={"pk": self.users.get("test-user").id}),
        )

    def test_user_setup(self):
        self.post(
            "test-user",
            reverse("user-setup", kwargs={"pk": self.users.get("test-user").id}),
            {"receive_notifications": "false"},
        )
        self.assertEqual(
            User.objects.get(pk=self.users.get("test-user").id).receive_notifications,
            False,
        )


class TestErrors(TestCase):
    def test_404(self):
        response = self.client.get(reverse("error", kwargs={"type": 404}))
        self.assertIn("errors/404.html", response.template_name)

    def test_403(self):
        response = self.client.get(reverse("error", kwargs={"type": 403}))
        self.assertIn("errors/403.html", response.template_name)

    def test_500(self):
        response = self.client.get(reverse("error", kwargs={"type": 500}))
        self.assertIn("errors/500.html", response.template_name)

    def test_500_func(self):
        request = RequestFactory().get("/error/500")
        response = error_500_handler(request)
        self.assertIn("errors/500.html", response.template_name)

    def test_404_post(self):
        response = self.client.post(reverse("error", kwargs={"type": 404}))
        self.assertEqual(response.templates[0].name, "errors/404.html")

    def test_403_post(self):
        response = self.client.post(reverse("error", kwargs={"type": 403}))
        self.assertEqual(response.templates[0].name, "errors/403.html")

    def test_500_post(self):
        response = self.client.post(reverse("error", kwargs={"type": 500}))
        self.assertEqual(response.templates[0].name, "errors/500.html")

    def test_invalid_type(self):
        response = self.client.get(reverse("error", kwargs={"type": 111}))
        self.assertIn("errors/404.html", response.template_name)
