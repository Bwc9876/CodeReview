from uuid import UUID

from django.test import TestCase

from Instructor.models import Rubric
from Main.models import val_uuid, Review
from Users.models import User
from tests.testing_base import BaseCase


class UserMethodsTest(TestCase):
    def test_user_session_str(self):
        self.assertEqual("AM Session", User.session_from_str("AM"))
        self.assertEqual("PM Session", User.session_from_str("PM"))

    def test_user_str(self):
        admin = User.objects.create_superuser(username="admin")
        test_user = User.objects.create_user(
            username="test", first_name="Test", last_name="User"
        )
        self.assertEqual(str(admin), "admin")
        self.assertEqual(str(test_user), "Test User")


class RubricMethodsTest(BaseCase):
    test_review = False

    def test_rubric_str(self):
        self.assertEqual(
            "Test Rubric (12 points)", str(Rubric.objects.get(name="Test Rubric"))
        )


class ValUUIDTest(TestCase):
    def test_valid(self):
        self.assertEqual(
            UUID("f6c0be2f-b12c-4702-b76b-6d497c1f2a7c"),
            val_uuid("f6c0be2f-b12c-4702-b76b-6d497c1f2a7c"),
        )

    def test_invalid(self):
        self.assertIsNone(val_uuid("bad uuid"))


class BaseModelMethodTest(TestCase):
    def test_max_length(self):
        self.assertEqual(Review.max_length("schoology_id"), 10)


class ReviewMethodTest(BaseCase):
    test_users = BaseCase.USER_STUDENT_REVIEWER

    test_review_student = "student"
    test_review_reviewer = "reviewer"

    def setUp(self) -> None:
        super(ReviewMethodTest, self).setUp()
        self.set_test_review_status(Review.Status.ASSIGNED)
        self.post_test_review("reviewer", "review-grade", {"scores": "[5,2]", "is_draft": "false"})
        self.review = Review.objects.get(id=self.review.id)
        self.set_user_full_name("student", "Test", "Student")

    def test_score_fraction(self):
        self.assertEqual(self.review.score_fraction(), "7.0/12.0")

    def test_score_fraction_not_complete(self):
        self.set_test_review_status(Review.Status.ASSIGNED)
        self.assertIsNone(self.review.score_fraction())

    def test_str(self):
        self.assertEqual(str(self.review), "Review from Test Student")

    def test_get_status_from_str(self):
        self.assertEqual("Open", Review.get_status_from_string("O"))
        self.assertEqual("Taken", Review.get_status_from_string("A"))
        self.assertEqual("Completed", Review.get_status_from_string("C"))
