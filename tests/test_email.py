from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse

from Instructor.models import Rubric
from Main.models import Review
from Users.models import User

with open("tests/test_rubric.json", 'r') as file:
    test_json = file.read()


class TestEmail(TestCase):

    def create_user_matrix(self):
        users = {
            'reviewer-affiliated': User.objects.create_user("reviewer-affiliated", is_reviewer=True),
            'student-affiliated': User.objects.create_user("student-affiliated"),
            'reviewer-not': User.objects.create_user("reviewer-not", is_reviewer=True),
            'student-not': User.objects.create_user("student-not"),
            'super': User.objects.create_superuser("test-instructor"),
        }
        for key in users.keys():
            users[key].email = f"{key}@example.com"
            users[key].save()
        self.users = users

    def create_client_matrix(self):
        clients = {}
        for key in self.users.keys():
            val = self.users.get(key)
            new_client = Client()
            new_client.force_login(val)
            clients[key] = new_client
        self.clients = clients

    def setUp(self) -> None:
        self.create_user_matrix()
        self.create_client_matrix()
        self.clients['super'].post(reverse("rubric-create"), {'name': "Test Review Rubric", 'rubric': test_json})
        self.rubric = Rubric.objects.get(name="Test Review Rubric")

    def test_created(self) -> None:
        self.clients['student-affiliated'].post(reverse("review-create"), {"schoology_id": "12.34.56", "rubric": self.rubric.id})
        self.assertEqual(len(mail.outbox), 2)
        for msg in mail.outbox:
            self.assertTrue(msg.to[0] == self.users['reviewer-affiliated'].email or msg.to[0] == self.users['reviewer-not'].email,
                            msg=f"{msg.to[0]} is not a reviewer")
            self.assertEqual(msg.subject, "AM | Review created by student-affiliated")

    def test_claimed(self) -> None:
        self.review = Review.objects.create(schoology_id="12.34.56", student=self.users['student-affiliated'], rubric=self.rubric)
        self.clients['reviewer-affiliated'].post(reverse("review-claim", kwargs={'pk': self.review.id}))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.users['super'].email)
        self.assertEqual(mail.outbox[0].subject, "AM | Review accepted by reviewer-affiliated")

    def test_completed(self) -> None:
        self.review = Review.objects.create(schoology_id="12.34.56",
                                            student=self.users['student-affiliated'], rubric=self.rubric,
                                            reviewer=self.users['reviewer-affiliated'], status=Review.Status.ASSIGNED)
        self.clients['reviewer-affiliated'].post(reverse("review-grade", kwargs={'pk': self.review.id}),
                                                 {"scores": "[10,2]", "additional_comments": ""})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.users['super'].email)
        self.assertEqual(mail.outbox[0].subject, "AM | Review completed by reviewer-affiliated")

    def test_session_checks(self) -> None:
        self.users['student-affiliated'].session = User.Session.PM
        self.users['student-affiliated'].save()
        self.clients['student-affiliated'].post(reverse("review-create"), {"schoology_id": "12.34.56", "rubric": self.rubric.id})
        self.assertEqual(len(mail.outbox), 0)

    def test_not_self(self) -> None:
        self.users['reviewer-not'].session = User.Session.PM
        self.users['reviewer-not'].save()
        self.clients['reviewer-not'].post(reverse("review-create"), {"schoology_id": "12.34.56", "rubric": self.rubric.id})
        self.assertEqual(len(mail.outbox), 0)
