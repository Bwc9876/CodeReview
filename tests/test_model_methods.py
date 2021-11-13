from uuid import UUID

from django.test import TestCase, Client
from django.urls import reverse

from Instructor.models import Rubric
from Main.models import val_uuid, Review
from Users.models import User

with open("tests/test_rubric.json", 'r') as file:
    test_json = file.read()


class UserMethodsTest(TestCase):

    def test_user_session_str(self):
        self.assertEqual("AM Session", User.session_from_str("AM"))
        self.assertEqual("PM Session", User.session_from_str("PM"))

    def test_user_str(self):
        admin = User.objects.create_superuser(username="admin")
        test_user = User.objects.create_user(username="test", first_name="Test", last_name="User")
        self.assertEqual(str(admin), "admin")
        self.assertEqual(str(test_user), "Test User")


class RubricMethodsTest(TestCase):

    def test_rubric_str(self):
        admin = User.objects.create_superuser(username="admin")
        c = Client()
        c.force_login(admin)
        c.post(reverse('rubric-create'), {'name': "Test Rubric", "rubric": test_json})
        self.assertEqual("Test Rubric", str(Rubric.objects.get(name="Test Rubric")))


class ValUUIDTest(TestCase):

    def test_valid(self):
        self.assertEqual(UUID("f6c0be2f-b12c-4702-b76b-6d497c1f2a7c"), val_uuid("f6c0be2f-b12c-4702-b76b-6d497c1f2a7c"))

    def test_invalid(self):
        self.assertIsNone(val_uuid("bad uuid"))


class BaseModelMethodTest(TestCase):

    def test_max_length(self):
        self.assertEqual(Review.max_length('schoology_id'), 10)


class ReviewMethodTest(TestCase):

    def create_user_matrix(self) -> None:
        users = {
            'reviewer': User.objects.create_user("reviewer-affiliated", is_reviewer=True),
            'student': User.objects.create_user("student-affiliated", first_name="Test", last_name="Student"),
            'super': User.objects.create_superuser("test-instructor"),
        }
        self.users = users

    def create_client_matrix(self) -> None:
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
        self.review = Review.objects.create(rubric=self.rubric, schoology_id="03.04.05",
                                            student=self.users['student'],
                                            reviewer=self.users['reviewer'], status=Review.Status.ASSIGNED)
        self.clients['reviewer'].post(reverse('review-grade', kwargs={'pk': self.review.id}), {'scores': "[5,2]"})

    def test_score_fraction(self):
        self.assertEqual(Review.objects.get(id=self.review.id).score_fraction(), "7.0/12.0")

    def test_score_fraction_not_complete(self):
        self.review.status = Review.Status.ASSIGNED
        self.review.save()
        self.assertIsNone(Review.objects.get(id=self.review.id).score_fraction())

    def test_str(self):
        self.assertEqual(str(self.review), "Review from Test Student")

    def test_get_status_from_str(self):
        self.assertEqual("Open", Review.get_status_from_string('O'))
        self.assertEqual("Taken", Review.get_status_from_string('A'))
        self.assertEqual("Completed", Review.get_status_from_string('C'))
